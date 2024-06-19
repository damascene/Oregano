package org.oregano.oregano3

import android.app.Dialog
import android.content.Intent
import android.os.Bundle
import android.text.Selection
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.SeekBar
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.DialogFragment
import androidx.fragment.app.Fragment
import androidx.viewbinding.ViewBinding
import com.chaquo.python.Kwarg
import com.chaquo.python.PyException
import com.chaquo.python.PyObject
import com.google.zxing.integration.android.IntentIntegrator
import org.oregano.oregano3.databinding.ChooseKeystoreBinding
import org.oregano.oregano3.databinding.MultisigCosignersBinding
import org.oregano.oregano3.databinding.ShowMasterKeyBinding
import org.oregano.oregano3.databinding.WalletNew2Binding
import org.oregano.oregano3.databinding.WalletNewBinding
import kotlin.properties.Delegates.notNull


val libKeystore by lazy { libMod("keystore") }
val libWallet by lazy { libMod("wallet") }

val MAX_COSIGNERS = 15
val COSIGNER_OFFSET = 2 // min. number of multisig cosigners = 2
val SIGNATURE_OFFSET = 1 // min. number of req. multisig signatures = 1

class NewWalletDialog1 : AlertDialogFragment() {
    private var _binding: WalletNewBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        super.onCreateView(inflater, container, savedInstanceState)
        return binding.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    override fun onBuildDialog(builder: AlertDialog.Builder) {
        _binding = WalletNewBinding.inflate(LayoutInflater.from(context))
        builder.setTitle(R.string.New_wallet)
            .setView(binding.root)
            .setPositiveButton(R.string.next, null)
            .setNegativeButton(R.string.cancel, null)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding.spnWalletType.adapter = MenuAdapter(context!!, R.menu.wallet_kind)
    }

    override fun onShowDialog() {
        dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
            try {
                val name = binding.etName.text.toString()
                validateWalletName(name)
                val password = confirmPassword(dialog, binding.etNewPassword, binding.etConfirmPassword)
                val arguments = Bundle().apply {
                    putString("name", name)
                    putString("password", password)
                }

                val nextDialog = when (binding.spnWalletType.selectedItemId.toInt()) {
                    R.id.menuStandardWallet -> {
                        KeystoreDialog()
                    }
                    R.id.menuMultisigWallet -> {
                        CosignerDialog()
                    }
                    R.id.menuImport -> {
                        NewWalletImportDialog()
                    }
                    else -> {
                        throw Exception("Unknown item: ${binding.spnWalletType.selectedItem}")
                    }
                }
                showDialog(this, nextDialog.apply { setArguments(arguments) })
            } catch (e: ToastException) { e.show() }
        }
    }
}

fun closeDialogs(targetFragment: Fragment) {
    val sfm = targetFragment.activity!!.supportFragmentManager
    val fragments = sfm.fragments
    for (frag in fragments) {
        if (frag is DialogFragment) {
            frag.dismiss()
        }
    }
}

fun validateFilename(name: String) {
    if (name.isEmpty()) {
        throw ToastException(R.string.name_is)
    }
    if (name.contains("/")) {
        throw ToastException(R.string.filenames_cannot)
    }
    if (name.toByteArray().size > 200) {
        // The filesystem limit is probably 255, but we need to leave room for the temporary
        // filename suffix.
        throw ToastException(R.string.filename_is)
    }
}

fun validateWalletName(name: String) {
    validateFilename(name)
    if (daemonModel.listWallets().contains(name)) {
        throw ToastException(R.string.a_wallet_with_that_name_already_exists_please_enter)
    }
}


// Also called from PasswordChangeDialog.
fun confirmPassword(dialog: Dialog, etNewPassword: EditText, etConfirmPassword: EditText): String {
    val password = etNewPassword.text.toString()
    if (password.isEmpty()) throw ToastException(R.string.Enter_password, Toast.LENGTH_SHORT)
    if (password != etConfirmPassword.text.toString()) {
        throw ToastException(R.string.wallet_passwords)
    }
    return password
}

// Choose the way of generating the wallet (new seed, import seed, etc.)
class KeystoreDialog : AlertDialogFragment() {
    private var _binding: ChooseKeystoreBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        super.onCreateView(inflater, container, savedInstanceState)
        return binding.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    override fun onBuildDialog(builder: AlertDialog.Builder) {
        _binding = ChooseKeystoreBinding.inflate(LayoutInflater.from(context))
        builder.setTitle(R.string.New_wallet)
            .setView(binding.root)
            .setPositiveButton(android.R.string.ok, null)
            .setNegativeButton(R.string.back, null)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        updateArguments(arguments!!)
    }

    fun updateArguments(arguments: Bundle?) {
        super.setArguments(arguments)

        /* Handle dialog title for cosigners */
        val keystores = arguments!!.getStringArrayList("keystores")
        if (keystores != null) {
            dialog.setTitle(multisigTitle(arguments))
        }

        val keystoreMenu: Int
        if (keystores != null && keystores.size != 0) {
            keystoreMenu = R.menu.cosigner_type
            binding.keystoreDesc.setText(R.string.add_a)
        } else {
            binding.keystoreDesc.setText(R.string.do_you_want_to_create)
            keystoreMenu = R.menu.wallet_type
        }
        binding.spnType.adapter = MenuAdapter(context!!, keystoreMenu)
    }

    override fun onShowDialog() {
        dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
            try {
                val nextDialog: DialogFragment
                val nextArguments = Bundle(arguments)
                val keystoreType = binding.spnType.selectedItemId.toInt()
                if (keystoreType in listOf(R.id.menuCreateSeed, R.id.menuRestoreSeed)) {
                    nextDialog = NewWalletSeedDialog()
                    val seed = if (keystoreType == R.id.menuCreateSeed)
                        daemonModel.commands.callAttr("make_seed").toString()
                    else null
                    nextArguments.putString("seed", seed)
                } else if (keystoreType in listOf(R.id.menuImportMaster)) {
                    nextDialog = NewWalletImportMasterDialog()
                } else {
                    throw Exception("Unknown item: ${binding.spnType.selectedItem}")
                }
                nextDialog.setArguments(nextArguments)
                showDialog(this, nextDialog)
            } catch (e: ToastException) { e.show() }
        }
    }
}

private fun multisigTitle(arguments: Bundle) =
    (app.getString(R.string.Add_cosigner) + " " +
     app.getString(R.string.__1_d, arguments.getStringArrayList("keystores")!!.size + 1,
                   arguments.getInt("cosigners")))


abstract class NewWalletDialog2 : TaskLauncherDialog<PyObject?>() {
    var input: String by notNull()
    private var _binding: WalletNew2Binding? = null
    public val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        super.onCreateView(inflater, container, savedInstanceState)
        return binding.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    override fun onBuildDialog(builder: AlertDialog.Builder) {
        _binding = WalletNew2Binding.inflate(LayoutInflater.from(context))
        builder.setTitle(R.string.New_wallet)
            .setView(binding.root)
            .setPositiveButton(android.R.string.ok, null)
            .setNegativeButton(R.string.back, null)

        // Update dialog title based on wallet type and/or current cosigner
        val keystores = arguments!!.getStringArrayList("keystores")
        if (keystores != null && keystores.size != 0) {
            builder.setTitle(multisigTitle(arguments!!))
        } else {
            builder.setTitle(R.string.New_wallet)
        }
    }

    override fun onPreExecute() {
        input = binding.etInput.text.toString()
    }

    override fun doInBackground(): PyObject? {
        val name = arguments!!.getString("name")!!
        val password = arguments!!.getString("password")!!
        val ks = onCreateWallet(name, password)

        /**
         * For multisig wallets, wait until all cosigners have been added,
         * and then create and load the multisig wallet.
         *
         * Otherwise, load the created wallet.
         */
        val keystores = updatedKeystores(arguments!!, ks)
        if (keystores != null) {
            val numCosigners = arguments!!.getInt("cosigners")
            val numSignatures = arguments!!.getInt("signatures")

            if (keystores.size == numCosigners) {
                daemonModel.commands.callAttr(
                        "create_multisig", name, password,
                        Kwarg("keystores", keystores.toArray()),
                        Kwarg("cosigners", numCosigners),
                        Kwarg("signatures", numSignatures)
                )
                daemonModel.loadWallet(name, password)
            }
        } else {
            daemonModel.loadWallet(name, password)
        }

        return ks
    }

    abstract fun onCreateWallet(name: String, password: String): PyObject?

    override fun onPostExecute(result: PyObject?) {
        val keystores = updatedKeystores(arguments!!, result)
        val name = arguments!!.getString("name")

        /**
         * For multisig wallets, we need to first show the master key to the 1st cosigner, and
         * then prompt for data for all other cosigners by calling the KeystoreDialog again.
         */
        if (keystores != null) {
            val currentCosigner = keystores.size
            val numCosigners = arguments!!.getInt("cosigners")

            if (currentCosigner < numCosigners) {
                val keystoreDialog = targetFragment as KeystoreDialog
                val nextArguments = Bundle(arguments).apply {
                    putStringArrayList("keystores", keystores)
                }
                // For the first cosigner we show the master public key so they can share it.
                if (currentCosigner == 1) {
                    val nextDialog = MasterPublicKeyDialog()
                    nextDialog.setArguments(nextArguments.apply {
                        val masterKey = result!!.callAttr("get", "xpub").toString()
                        putString("masterKey", masterKey)
                    })
                    showDialog(keystoreDialog, nextDialog)
                } else {
                    // Update dialog title and arguments for the next cosigner
                    keystoreDialog.updateArguments(nextArguments)
                }
            } else { // last cosigner done; finalize wallet
                selectWallet(targetFragment!!, name)
            }
        } else {
            // In a standard wallet, close the dialogs and open the newly created wallet.
            selectWallet(targetFragment!!, name)
        }
    }

    private fun selectWallet(targetFragment: Fragment, name: String?) {
        closeDialogs(targetFragment)
        daemonModel.commands.callAttr("select_wallet", name)
        (activity as MainActivity).updateDrawer()
    }
}


class NewWalletSeedDialog : NewWalletDialog2() {
    var passphrase: String by notNull()
    var bip39: Boolean by notNull()
    var derivation: String? = null

    override fun onShowDialog() {
        super.onShowDialog()
        setupSeedDialog(this, binding)
        if (arguments!!.getString("seed") == null) {  // Restore from seed
            binding.bip39Panel.visibility = View.VISIBLE
            val bip39Listener = { binding.etDerivation.isEnabled = binding.swBip39.isChecked }
            binding.swBip39.setOnCheckedChangeListener { _, _ -> bip39Listener() }
            bip39Listener()
        }
    }

    override fun onPreExecute() {
        super.onPreExecute()
        passphrase = binding.etPassphrase.text.toString()
        bip39 = binding.swBip39.isChecked
        if (bip39) {
            derivation = binding.etDerivation.text.toString()
        }
    }

    override fun onCreateWallet(name: String, password: String): PyObject? {
        try {
            if (derivation != null &&
                !libBitcoin.callAttr("is_bip32_derivation", derivation).toBoolean()) {
                throw ToastException(R.string.Derivation_invalid)
            }

            val multisig = arguments!!.containsKey("keystores")
            return daemonModel.commands.callAttr(
                "create", name, password,
                Kwarg("seed", input),
                Kwarg("passphrase", passphrase),
                Kwarg("multisig", multisig),
                Kwarg("bip39_derivation", derivation))
        } catch (e: PyException) {
            if (e.message!!.startsWith("InvalidSeed")) {
                throw ToastException(R.string.the_seed_you_entered_does_not_appear)
            }
            throw e
        }
    }
}


class NewWalletImportDialog : NewWalletDialog2() {
    override fun onBuildDialog(builder: AlertDialog.Builder) {
        super.onBuildDialog(builder)
        builder.setNeutralButton(R.string.scan_qr, null)
    }

    override fun onShowDialog() {
        super.onShowDialog()
        binding.tvPrompt.setText(R.string.enter_a_list_of_ergon)
        dialog.getButton(AlertDialog.BUTTON_NEUTRAL).setOnClickListener { scanQR(this) }
    }

    override fun onCreateWallet(name: String, password: String): PyObject? {
        var foundAddress = false
        var foundPrivkey = false
        for (word in input.split(Regex("\\s+"))) {
            if (word.isEmpty()) {
                // Can happen at start or end of list.
            } else if (clsAddress.callAttr("is_valid", word).toBoolean()) {
                foundAddress = true
            } else {
                try {
                    // Use the same function as the wallet creation process (#2133).
                    libAddress.get("PublicKey")!!.callAttr("from_WIF_privkey", word)
                    foundPrivkey = true
                } catch (e: PyException) {
                    throw ToastException(getString(R.string.not_a_valid, word))
                }
            }
        }

        return if (foundAddress) {
            if (foundPrivkey) {
                throw ToastException(
                    R.string.cannot_specify_private_keys_and_addresses_in_the_same_wallet)
            }
            daemonModel.commands.callAttr("create", name, password, Kwarg("addresses", input))
        } else if (foundPrivkey) {
            daemonModel.commands.callAttr("create", name, password, Kwarg("privkeys", input))
        } else {
            throw ToastException(R.string.you_appear_to_have_entered_no)
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        val result = IntentIntegrator.parseActivityResult(requestCode, resultCode, data)
        if (result != null && result.contents != null) {
            appendLine(binding.etInput, result.contents)
        } else {
            super.onActivityResult(requestCode, resultCode, data)
        }
    }
}

fun appendLine(et: EditText, str: String) {
    val text = et.text
    if (!text.isEmpty() && !text.endsWith("\n")) {
        text.append("\n")
    }
    text.append(str)
    Selection.setSelection(text, text.length)
}


class NewWalletImportMasterDialog : NewWalletDialog2() {
    override fun onBuildDialog(builder: AlertDialog.Builder) {
        super.onBuildDialog(builder)
        builder.setNeutralButton(R.string.scan_qr, null)
    }

    override fun onShowDialog() {
        super.onShowDialog()
        val keystores = arguments!!.getStringArrayList("keystores")

        val keyPrompt = if (keystores != null && keystores.size != 0) {
            getString(R.string.please_enter_the_master_public_key_xpub) + " " +
            getString(R.string.enter_their)
        } else {
            getString(R.string.to_create_a_watching) + " " +
            getString(R.string.to_create_a_spending)
        }
        binding.tvPrompt.setText(keyPrompt)

        dialog.getButton(AlertDialog.BUTTON_NEUTRAL).setOnClickListener { scanQR(this) }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        val result = IntentIntegrator.parseActivityResult(requestCode, resultCode, data)
        if (result != null && result.contents != null) {
            binding.etInput.setText(result.contents)
            binding.etInput.setSelection(result.contents.length)
        } else {
            super.onActivityResult(requestCode, resultCode, data)
        }
    }

    override fun onCreateWallet(name: String, password: String): PyObject? {
        val key = input.trim()
        if (libKeystore.callAttr("is_bip32_key", key).toBoolean()) {
            val multisig = arguments!!.containsKey("keystores")
            return daemonModel.commands.callAttr(
                "create", name, password,
                Kwarg("master", key),
                Kwarg("multisig", multisig)
            )
        } else {
            throw ToastException(R.string.please_specify)
        }
    }
}


fun setupSeedDialog(fragment: AlertDialogFragment, binding: WalletNew2Binding) {
    with (fragment) {
        val seed = fragment.arguments!!.getString("seed")
        if (seed == null) {
            // Import
            binding.tvPrompt.setText(R.string.please_enter_your_seed_phrase)
        } else {
            // Generate or display
            binding.tvPrompt.setText(seedAdvice(seed))
            binding.etInput.setText(seed)
            binding.etInput.setFocusable(false)
        }

        val passphrase = fragment.arguments!!.getString("passphrase")
        if (passphrase == null) {
            // Import or generate
            binding.passphrasePanel.visibility = View.VISIBLE
            binding.tvPassphrasePrompt.setText(app.getString(R.string.you_may_extend) + " " +
                                       app.getString(R.string.if_you_are))
        } else {
            // Display
            if (passphrase.isNotEmpty()) {
                binding.passphrasePanel.visibility = View.VISIBLE
                binding.tvPassphrasePrompt.setText(R.string.passphrase)
                binding.etPassphrase.setText(passphrase)
                binding.etPassphrase.setFocusable(false)
            }
        }
    }
}

// Choose the number of multi-sig wallet cosigners
class CosignerDialog : AlertDialogFragment() {
    private var _binding: MultisigCosignersBinding? = null
    private val binding get() = _binding!!

    override fun onBuildDialog(builder: AlertDialog.Builder) {
        _binding = MultisigCosignersBinding.inflate(LayoutInflater.from(context))
        builder.setTitle(R.string.Multi_signature)
                .setView(binding.root)
                .setPositiveButton(R.string.next, null)
                .setNegativeButton(R.string.cancel, null)
    }

    val numCosigners: Int
        get() = binding.sbCosigners.progress + COSIGNER_OFFSET

    val numSignatures: Int
        get() = binding.sbSignatures.progress + SIGNATURE_OFFSET

    override fun onFirstShowDialog() {
        super.onFirstShowDialog()

        with (binding.sbCosigners) {
            progress = 0
        }

        with (binding.sbSignatures) {
            progress = numCosigners - SIGNATURE_OFFSET
            max = numCosigners - SIGNATURE_OFFSET
        }
    }

    override fun onShowDialog() {
        super.onShowDialog()
        updateUi()

        // Handle the total number of cosigners
        with (binding.sbCosigners) {
            max = MAX_COSIGNERS - COSIGNER_OFFSET

            setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
                override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                    updateUi()
                }

                override fun onStartTrackingTouch(seekBar: SeekBar?) {}
                override fun onStopTrackingTouch(seekBar: SeekBar) {}
            })
        }

        // Handle the number of required signatures
        with (binding.sbSignatures) {
            setOnSeekBarChangeListener(object: SeekBar.OnSeekBarChangeListener {
                override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                    updateUi()
                }

                override fun onStartTrackingTouch(seekBar: SeekBar?) {}
                override fun onStopTrackingTouch(seekBar: SeekBar?) {}
            })
        }

        dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
            try {
                val nextDialog = KeystoreDialog()
                val nextArguments = Bundle(arguments)
                nextArguments.putInt("cosigners", numCosigners)
                nextArguments.putInt("signatures", numSignatures)
                // The "keystores" argument contains keystore data for multiple cosigners
                // in multisig wallets. It is used throughout the file to check if dealing
                // with a multisig wallet and to get relevant cosigner data.
                nextArguments.putStringArrayList("keystores", ArrayList<String>())

                nextDialog.setArguments(nextArguments)
                showDialog(this, nextDialog)
            } catch (e: ToastException) {
                e.show()
            }
        }
    }

    private fun updateUi() {
        binding.tvCosigners.text = getString(R.string.from_cosigners, numCosigners)
        binding.tvSignatures.text = getString(R.string.require_signatures, numSignatures)
        binding.sbSignatures.max = numCosigners - SIGNATURE_OFFSET
    }
}

/**
 * View and copy the master public key of the (multisig) wallet.
 */
class MasterPublicKeyDialog : AlertDialogFragment() {
    private var _binding: ShowMasterKeyBinding? = null
    private val binding get() = _binding!!

    override fun onBuildDialog(builder: AlertDialog.Builder) {
        _binding = ShowMasterKeyBinding.inflate(LayoutInflater.from(context))
        builder.setView(binding.root)
                .setPositiveButton(R.string.next, null)
                .setNegativeButton(R.string.back, null)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding.fabCopyMasterKey.setOnClickListener {
            copyToClipboard(binding.walletMasterKey.text, R.string.Master_public_key)
        }
    }

    override fun onShowDialog() {
        super.onShowDialog()
        binding.walletMasterKey.setText(arguments!!.getString("masterKey"))
        binding.walletMasterKey.setFocusable(false)

        dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
            dismiss()
            (targetFragment as KeystoreDialog).updateArguments(Bundle(arguments))
        }
    }
}

fun seedAdvice(seed: String): String {
    return app.getString(R.string.please_save, seed.split(" ").size) + " " +
           app.getString(R.string.this_seed_will) + " " +
           app.getString(R.string.never_disclose)
}

/**
 * Returns the updated "keystores" array list for multisig wallets, used to check whether to
 * finalize multisig wallet creation (or if it is a multisig wallet at all).
 * In intermediary steps (adding non-final cosigners), the updated keystores will be stored into
 * a dialog argument in onPostExecute().
 */
fun updatedKeystores(arguments: Bundle, ks: PyObject?): ArrayList<String>? {
    val keystores = arguments.getStringArrayList("keystores")
    if (keystores != null) {
        val newKeystores = ArrayList<String>(keystores)
        if (ks != null) {
            newKeystores.add(ks.toString())
        }
        return newKeystores
    }
    return null
}
