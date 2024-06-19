package org.oregano.oregano3

import android.content.ClipboardManager
import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.DialogFragment
import androidx.viewbinding.ViewBinding
import com.chaquo.python.Kwarg
import com.chaquo.python.PyException
import com.chaquo.python.PyObject
import com.chaquo.python.PyObject.fromJava
import com.google.zxing.integration.android.IntentIntegrator
import org.oregano.oregano3.databinding.LoadBinding
import org.oregano.oregano3.databinding.SignedTransactionBinding
import org.oregano.oregano3.databinding.SweepBinding
import org.oregano.oregano3.databinding.WalletInformationBinding


val libTransaction by lazy { libMod("transaction") }


// This provides a dialog to allow users to input a string, which is then broadcast
// on the bitcoin cash network. Strings are not validated,
// but broadcast_transaction should throw error which is toasted.
// Valid transaction quickly show up in transactions.

class ColdLoadDialog : AlertDialogFragment() {
    private var _binding: LoadBinding? = null
    private val binding get() = _binding!!

    override fun onBuildDialog(builder: AlertDialog.Builder) {
        _binding = LoadBinding.inflate(LayoutInflater.from(context))
        builder.setTitle(R.string.load_transaction)
                .setView(binding.root)
                .setNegativeButton(android.R.string.cancel, null)
                .setNeutralButton(R.string.scan_qr, null)
                .setPositiveButton(R.string.OK, null)
    }

    override fun onShowDialog() {
        super.onShowDialog()
        binding.etTransaction.addAfterTextChangedListener{ updateUI() }
        updateUI()

        dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener { onOK() }
        dialog.getButton(AlertDialog.BUTTON_NEUTRAL).setOnClickListener { scanQR(this) }
        binding.btnPaste.setOnClickListener {
            val clipdata = getSystemService(ClipboardManager::class).primaryClip
            if (clipdata != null && clipdata.getItemCount() > 0) {
                val cliptext = clipdata.getItemAt(0)
                binding.etTransaction.setText(cliptext.text)
            }
        }
    }

    private fun updateUI() {
        val tx = txFromHex(binding.etTransaction.text.toString())
        updateStatusText(binding.tvStatus, tx)
        dialog.getButton(AlertDialog.BUTTON_POSITIVE).isEnabled =
            canSign(tx) || canBroadcast(tx)
    }

    // Receives the result of a QR scan.
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        val result = IntentIntegrator.parseActivityResult(requestCode, resultCode, data)
        if (result != null && result.contents != null) {
            // Try to decode the QR content as Base43; if that fails, treat it as is
            val txHex: String = try {
                baseDecode(result.contents, 43)
            } catch (e: PyException) {
                result.contents
            }
            binding.etTransaction.setText(txHex)
        } else {
            super.onActivityResult(requestCode, resultCode, data)
        }
    }

    fun onOK() {
        val txHex = binding.etTransaction.text.toString()
        val tx = txFromHex(txHex)

        try {
            if (canBroadcast(tx)) {
                showDialog(this, SignedTransactionDialog().apply { arguments = Bundle().apply {
                    putString("txHex", txHex)
                }})
                dismiss()
            } else {
                signLoadedTransaction(txHex)
            }
        } catch (e: ToastException) {
            e.show()
        }
    }

    private fun signLoadedTransaction(txHex: String) {
        val arguments = Bundle().apply {
            putString("txHex", txHex)
            putBoolean("unbroadcasted", true)
        }
        val dialog = SendDialog()
        showDialog(this, dialog.apply { setArguments(arguments) })
    }
}

private fun updateStatusText(idTxStatus: TextView, tx: PyObject) {
    try {
        val txInfo = daemonModel.wallet!!.callAttr("get_tx_info", tx)
        if (txInfo["amount"] == null && !canBroadcast(tx)) {
            idTxStatus.setText(R.string.transaction_unrelated)
        } else {
            idTxStatus.setText(txInfo["status"].toString())
        }
    } catch (e: PyException) {
        idTxStatus.setText(R.string.invalid)
    }
}


class SignedTransactionDialog : TaskLauncherDialog<Unit>() {
    private var _binding: SignedTransactionBinding? = null
    private val binding get() = _binding!!

    private val tx: PyObject by lazy {
        txFromHex(arguments!!.getString("txHex")!!)
    }
    private lateinit var description: String

    override fun onBuildDialog(builder: AlertDialog.Builder) {
        _binding = SignedTransactionBinding.inflate(LayoutInflater.from(context))
        builder.setView(binding.root)
               .setNegativeButton(R.string.close, null)
               .setPositiveButton(R.string.send, null)
    }

    override fun onShowDialog() {
        super.onShowDialog()

        binding.fabCopy.setOnClickListener {
            copyToClipboard(tx.toString(), R.string.transaction)
        }
        showQR(binding.imgQR, baseEncode(tx.toString(), 43))
        updateStatusText(binding.tvStatus, tx)

        if (!canBroadcast(tx)) {
            hideDescription(this, binding.tvDescriptionLabel, binding.etDescription)
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).isEnabled = false
        }
    }

    override fun onPreExecute() {
        description = binding.etDescription.text.toString()
    }

    override fun doInBackground() {
        broadcastTransaction(daemonModel.wallet!!, tx, description)
    }

    override fun onPostExecute(result: Unit) {
        toast(R.string.payment_sent, Toast.LENGTH_SHORT)
    }
}

fun hideDescription(dialog: DialogFragment, descriptionLabel: TextView, description: TextView) {
    for (view in listOf(descriptionLabel, description)) {
        view.visibility = View.GONE
    }
}


class SweepDialog : TaskLauncherDialog<PyObject>() {
    private var _binding: SweepBinding? = null
    private val binding get() = _binding!!

    lateinit var input: String

    init {
        dismissAfterExecute = false
    }

    override fun onBuildDialog(builder: AlertDialog.Builder) {
        _binding = SweepBinding.inflate(LayoutInflater.from(context))
        builder.setTitle(R.string.sweep_private)
            .setView(binding.root)
            .setNeutralButton(R.string.scan_qr, null)
            .setNegativeButton(android.R.string.cancel, null)
            .setPositiveButton(android.R.string.ok, null)
    }

    override fun onShowDialog() {
        super.onShowDialog()
        dialog.getButton(AlertDialog.BUTTON_NEUTRAL).setOnClickListener { scanQR(this) }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        val result = IntentIntegrator.parseActivityResult(requestCode, resultCode, data)
        if (result != null && result.contents != null) {
            appendLine(binding.etInput, result.contents)
        } else {
            super.onActivityResult(requestCode, resultCode, data)
        }
    }

    override fun onPreExecute() {
        input = binding.etInput.text.toString()
    }

    override fun doInBackground(): PyObject {
        daemonModel.assertConnected()
        val privkeys = input.split(Regex("\\s+")).filter { !it.isEmpty() }.toTypedArray()
        try {
            return libWallet.callAttr("sweep_preparations", privkeys, daemonModel.network)
        } catch (e: PyException) {
            throw ToastException(e)
        }
    }

    override fun onPostExecute(result: PyObject) {
        // Convert objects to serializable form so we can pass them in an argument.
        val inputs = result.asList()[0]
        for (i in inputs.asList()) {
            val iMap = i.asMap()
            iMap[fromJava("address")] = fromJava(iMap[fromJava("address")].toString())
        }

        val wallet = daemonModel.wallet!!
        try {
            showDialog(this, SendDialog().setArguments {
                putString("address", wallet.callAttr("get_receiving_address").toString())
                putString("inputs", inputs.repr())
                putString("sweepKeypairs", result.asList()[1].repr())
            })
        } catch (e: ToastException) { e.show() }
    }
}


fun txFromHex(hex: String) =
    libTransaction.callAttr("Transaction", hex, Kwarg("sign_schnorr", signSchnorr()))!!

fun canSign(tx: PyObject): Boolean {
    return try {
        !tx.callAttr("is_complete").toBoolean() &&
        daemonModel.wallet!!.callAttr("can_sign", tx).toBoolean()
    } catch (e: PyException) {
        false
    }
}

fun canBroadcast(tx: PyObject): Boolean {
    return try {
        tx.callAttr("is_complete").toBoolean()
    } catch (e: PyException) {
        false
    }
}
