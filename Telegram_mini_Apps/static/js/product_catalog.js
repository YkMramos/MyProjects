const tg = window.Telegram.WebApp;
tg.setHeaderColor('#000');
tg.ready();
tg.expand();
tg.disableVerticalSwipes();
tg.BackButton.hide();

// Добавьте эту строку
tg.enableClosingConfirmation();


