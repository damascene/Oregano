package org.oregano.oregano3

import android.widget.Toast
import com.chaquo.python.Kwarg
import com.chaquo.python.PyException

// on_history is not included, because that's also generated by wallet updates.
val EXCHANGE_CALLBACKS = setOf("on_quotes")

val libExchange by lazy { libMod("exchange_rate") }
val fiatUpdate = TriggerLiveData()

val fx by lazy { daemonModel.daemon.get("fx")!! }


fun initExchange() {
    settings.getString("currency").observeForever {
        fx.callAttr("set_currency", it)
    }
    settings.getString("use_exchange").observeForever {
        fx.callAttr("set_exchange", it)
    }
    with (fiatUpdate) {
        addSource(settings.getBoolean("use_exchange_rate"))
        addSource(settings.getString("currency"))
        addSource(settings.getString("use_exchange"))
    }
}


fun fiatEnabled() = fx.callAttr("is_enabled").toBoolean()


fun fiatToSatoshis(s: String): Long? {
    if (!fiatEnabled()) return null
    try {
        // toDouble accepts only the English number format: see comment in Util.kt.
        return fx.callAttr("fiat_to_amount", s.toDouble())?.toLong()
    } catch (e: NumberFormatException) {
        throw ToastException(R.string.Invalid_amount)
    } catch (e: PyException) {
        throw if (e.message!!.startsWith("OverflowError")) ToastException(e) else e
    }
}


fun formatSatoshisAndFiat(amount: Long, commas: Boolean): String {
    var result = formatSatoshisAndUnit(amount)
    val fiat = formatFiatAmount(amount, commas)
    if (fiat != null) {
        result += " ($fiat ${formatFiatUnit()})"
    }
    return result
}

fun formatFiatAmount(amount: Long, commas: Boolean): String? {
    if (!fiatEnabled()) return null
    val amountStr = fx.callAttr("format_amount", amount, Kwarg("commas", commas)).toString()
    return if (amountStr.isEmpty()) null else amountStr
}


fun formatFiatUnit(): String {
    return fx.callAttr("get_currency").toString()
}