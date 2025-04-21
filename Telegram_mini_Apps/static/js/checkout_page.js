        // Валидация только буквы для ФИО
        document.getElementById('lastname').addEventListener('input', function(e) {
            this.value = this.value.replace(/[^а-яА-ЯёЁa-zA-Z\s-]/g, '');
        });

        document.getElementById('firstname').addEventListener('input', function(e) {
            this.value = this.value.replace(/[^а-яА-ЯёЁa-zA-Z\s-]/g, '');
        });

        document.getElementById('middlename').addEventListener('input', function(e) {
            this.value = this.value.replace(/[^а-яА-ЯёЁa-zA-Z\s-]/g, '');
        });

        document.getElementById('phone').addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, ''); // Удаляем все нечисловые символы

            if (value.startsWith('7')) { 
                value = '+' + value; // Если уже начинается с 7, просто добавляем +
            } else if (value.startsWith('8')) { 
                value = '+7' + value.slice(1); // Если начинается с 8, заменяем на +7
            } else if (!value.startsWith('+7')) { 
                value = '+7' + value; // Если не начинается с +7, добавляем +7
            }

            e.target.value = value;
        });



        // Функция для возврата назад
        function goBack() {
            // Здесь можно добавить логику перехода на предыдущую страницу
            window.history.back();
        }

        // Выбор способа доставки
        function selectDeliveryOption(option) {
            const options = document.querySelectorAll('#delivery-options .radio-option');
            options.forEach(opt => opt.classList.remove('selected'));

            const selectedOption = document.querySelector(`#delivery-${option}`);
            selectedOption.checked = true;
            selectedOption.closest('.radio-option').classList.add('selected');

            // Показать/скрыть соответствующие способы оплаты
            updatePaymentOptions(option);
        }

        // Выбор способа оплаты
        function selectPaymentOption(option) {
            const options = document.querySelectorAll('#payment-options .radio-option:not(.hidden)');
            options.forEach(opt => opt.classList.remove('selected'));

            const selectedOption = document.querySelector(`#payment-${option}`);
            if (selectedOption && !selectedOption.closest('.radio-option').classList.contains('hidden')) {
                selectedOption.checked = true;
                selectedOption.closest('.radio-option').classList.add('selected');
            }
        }

        // Обновить доступные способы оплаты в зависимости от выбранного способа доставки
        function updatePaymentOptions(deliveryOption) {
            const pickupPaymentOption = document.getElementById('payment-pickup-option');
            const courierPaymentOption = document.getElementById('payment-courier-option');

            // Получаем выбранный в данный момент способ оплаты
            const selectedPayment = document.querySelector('input[name="payment"]:checked');
            let needSelectDefault = false;

            if (deliveryOption === 'pickup') {
                // Показываем оплату в пункте выдачи
                pickupPaymentOption.classList.remove('hidden');
                // Скрываем оплату при получении курьеру
                courierPaymentOption.classList.add('hidden');

                // Если был выбран способ оплаты, который теперь недоступен, нужно выбрать другой
                if (selectedPayment && selectedPayment.value === 'courier') {
                    needSelectDefault = true;
                }
            } else {
                // Скрываем оплату в пункте выдачи
                pickupPaymentOption.classList.add('hidden');
                // Показываем оплату при получении курьеру
                courierPaymentOption.classList.remove('hidden');

                // Если был выбран способ оплаты, который теперь недоступен, нужно выбрать другой
                if (selectedPayment && selectedPayment.value === 'pickup') {
                    needSelectDefault = true;
                }
            }

            // Если нужно выбрать другой способ оплаты
            if (needSelectDefault) {
                if (deliveryOption === 'pickup') {
                    // Выбираем оплату в пункте выдачи
                    document.getElementById('payment-pickup').checked = true;
                    selectPaymentOption('pickup');
                } else {
                    // Выбираем оплату при получении
                    document.getElementById('payment-courier').checked = true;
                    selectPaymentOption('courier');
                }
            }
        }

        // Валидация формы
        document.getElementById('orderForm').addEventListener('submit', function(e) {
            e.preventDefault();

            let isValid = true;

            // Валидация персональных данных
            const lastname = document.getElementById('lastname');
            const firstname = document.getElementById('firstname');

            if (!lastname.value.trim()) {
                showError(lastname, 'lastname-error');
                isValid = false;
            } else {
                hideError(lastname, 'lastname-error');
            }

            if (!firstname.value.trim()) {
                showError(firstname, 'firstname-error');
                isValid = false;
            } else {
                hideError(firstname, 'firstname-error');
            }

            // Валидация адреса
            const city = document.getElementById('city');
            const street = document.getElementById('street');
            const house = document.getElementById('house');

            if (!city.value.trim()) {
                showError(city, 'city-error');
                isValid = false;
            } else {
                hideError(city, 'city-error');
            }

            if (!street.value.trim()) {
                showError(street, 'street-error');
                isValid = false;
            } else {
                hideError(street, 'street-error');
            }

            if (!house.value.trim()) {
                showError(house, 'house-error');
                isValid = false;
            } else {
                hideError(house, 'house-error');
            }


            // Простая проверка email на наличие @ и .
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email.value)) {
                showError(email, 'email-error');
                isValid = false;
            } else {
                hideError(email, 'email-error');
            }

            if (isValid) {
                // Показать всплывающее сообщение и перенаправить через 2 секунды
                document.getElementById('outOfStockOverlay').classList.add('visible');

                // Мгновенный редирект
                window.location.href = "{% url 'telegram_miniapp' %}";
            }
        });

        function showError(input, errorId) {
            input.classList.add('error');
            document.getElementById(errorId).classList.add('visible');
        }

        function hideError(input, errorId) {
            input.classList.remove('error');
            document.getElementById(errorId).classList.remove('visible');
        }

        // Инициализация при загрузке страницы
        document.addEventListener('DOMContentLoaded', function() {
            // Инициализируем способ доставки (по умолчанию - курьер)
            selectDeliveryOption('courier');
        });