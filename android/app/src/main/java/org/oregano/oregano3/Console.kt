package org.oregano.oregano3

import android.app.Application
import android.os.Bundle
import android.text.InputType
import com.chaquo.python.utils.PythonConsoleActivity
import org.oregano.oregano3.databinding.ActivityConsoleBinding


val guiConsole by lazy { guiMod("console") }


class ECConsoleActivity : PythonConsoleActivity() {
    private lateinit var binding: ActivityConsoleBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityConsoleBinding.inflate(layoutInflater)
        // VISIBLE_PASSWORD is necessary to prevent some versions of the Google keyboard from
        // displaying the suggestion bar.
        binding.etInput.inputType = (InputType.TYPE_CLASS_TEXT +
                             InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS +
                             InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD)
    }

    override fun getTaskClass(): Class<out Task> {
        return Task::class.java
    }

    // Maintain REPL state unless the loop has been terminated, e.g. by typing `exit()`. Will
    // also hide previous activities in the back-stack, unless the activity is in its own task.
    override fun onBackPressed() {
        if (task.state == Thread.State.RUNNABLE) {
            moveTaskToBack(true)
        } else {
            super.onBackPressed()
        }
    }

    // =============================================================================================

    class Task(app: Application) : PythonConsoleActivity.Task(app) {

        override fun run() {
            guiConsole
                .callAttr("AndroidConsole", app, daemonModel.commands)
                .callAttr("interact")
        }
    }

}
