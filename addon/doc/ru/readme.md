# translateNvdaAddonsWithCrowdin

Цель этого дополнения - помочь переводчикам работать более эффективно при использовании этого [проекта перевода дополнений NVDA с помощью Crowdin](https://crowdin.com/project/nvdaaddons).

## Настройки

Though most translators won't need to use this feature, a dialog is provided to save the Crowdin token, and to select the directory where documentation and interface message files will be stored.
To open this dialog, go to NVDA menu, Preferences submenu, Settings dialog, Translate NVDA add-ons with Crowdin category.

Also, a gesture can be assigned to open the add-on settings from the Input Gestures dialog.

## Translate add-ons with Crowdin

This dialog can be accessed from NVDA menu, Tools submenu, or assigning a gesture from the Input gestures dialog.

The following controls are available:

- Комбинированный список для выбора языка перевода.
- Поле редактирования для фильтрации списка файлов, доступных для перевода.
- Список файлов с расширениями po и md. Это будет в фокусе при открытии диалога. Нажмите Enter, чтобы открыть выбранный файл.
- Кнопка открытия выбранного файла. Файл будет открыт в приложении, связанном с каждым типом файлов в вашей системе. В любом случае, как правило, документацию будет легче переводить из веб-интерфейса Crowdin.
- Кнопка для выгрузки выбранного переведённого файла.
- Кнопка для загрузки переводов на выбранный язык.
- Кнопка для загрузки всех переводов
- Кнопка закрытия диалога.

## Загрузка и выгрузка переводов

- Этот процесс может занять несколько минут и может быть недоступен, если вы достигнете лимита токенов Crowdin.
- NVDA может блокироваться в течение нескольких секунд при запуске этих процессов. После этого вы можете работать нормально, и после завершения процесса должно появиться сообщение