package org.oregano.oregano3

import android.app.Dialog
import android.content.Context
import android.text.Editable
import android.view.LayoutInflater
import android.view.View
import android.widget.EditText
import android.widget.TextView
import org.oregano.oregano3.databinding.AmountBoxBinding

class AmountBox(val binding: AmountBoxBinding) {
    private val fiatEnabled = fiatEnabled()
    private var updating = false  // Prevent infinite recursion.
    var listener: (() -> Unit)? = null

    init {
        binding.tvUnit.text = unitName
        if (fiatEnabled) {
            binding.tvFiatUnit.text = formatFiatUnit()
        } else {
            binding.tvFiatUnit.visibility = View.GONE
            binding.etFiat.visibility = View.GONE
        }

        for (et in listOf(binding.etAmount, binding.etFiat)) {
            et.addAfterTextChangedListener { s: Editable ->
                if (!updating) {
                    if (fiatEnabled) {
                        val etOther: EditText
                        val formatOther: () -> String
                        when (et) {
                            binding.etAmount -> {
                                etOther = binding.etFiat
                                formatOther = {
                                    formatFiatAmount(toSatoshis(s.toString()), commas=false) ?: ""
                                }
                            }
                            binding.etFiat -> {
                                etOther = binding.etAmount
                                formatOther = {
                                    val amount = fiatToSatoshis(s.toString())
                                    if (amount != null) formatSatoshis(amount) else ""
                                }
                            }
                            else -> throw RuntimeException("Unknown view")
                        }

                        try {
                            updating = true
                            etOther.setText(formatOther())
                            etOther.setSelection(etOther.text.length)
                        } catch (e: ToastException) {
                            etOther.setText("")
                        } finally {
                            updating = false
                        }
                    }
                    listener?.invoke()
                }
            }
        }
    }

    var amount: Long?
        get() {
            val amount = try {
                toSatoshis(binding.etAmount.text.toString())
            } catch (e: ToastException) {
                return null
            }
            // Both the Send and Request dialogs require a positive number.
            return if (amount <= 0) null else amount
        }
        set(amount) {
            if (amount == null) {
                binding.etAmount.setText("")
            } else {
                binding.etAmount.setText(formatSatoshis(amount))
                binding.etAmount.setSelection(binding.etAmount.text.length)
            }
        }

    var isEditable: Boolean
        get() = isEditable(binding.etAmount)
        set(editable) {
            for (et in listOf(binding.etAmount, binding.etFiat)) {
                setEditable(et, editable)
            }
        }

    /** We don't <requestFocus/> in the layout file, because in the Send dialog, initial focus
     * is normally on the address box. */
    fun requestFocus() = binding.etAmount.requestFocus()
}
