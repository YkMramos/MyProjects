    // Инициализация Telegram WebApp
const tg = window.Telegram.WebApp;
tg.setHeaderColor('#000');
tg.ready();
tg.expand();  // Расширяем на весь экран
tg.disableVerticalSwipes();
tg.BackButton.hide();
// Устанавливаем основной цвет




// Функция для загрузки начальной суммы корзины
function loadInitialCartTotal() {
    fetch('/cart/cart_total/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            // передавайте необходимые данные, если нужно
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const formattedPrice = formatPrice(data.total_price);
            updateTotalPrice(formattedPrice);
        } else {
            console.error('Ошибка при получении суммы корзины:', data.message);
        }
    })
    .catch(error => {
        console.error('Ошибка при загрузке начальной суммы корзины:', error);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const MIN_QUANTITY = 1;
    const MAX_QUANTITY = 15;
    loadInitialCartTotal(); 
    // Форматируем все цены на странице
    const priceElements = document.querySelectorAll('.product-price');
    priceElements.forEach(function(element) {
        const priceText = element.textContent.trim();
        const formattedPrice = formatPrice(priceText);
        element.textContent = formattedPrice + ' ₽';
    });

    // Находим все product-item элементы
    const productItems = document.querySelectorAll('.product-item');

    productItems.forEach(productItem => {
        const productId = productItem.dataset.productId;
     
        const quantityDisplay = productItem.querySelector('.quantity-number');
        const decreaseButton = productItem.querySelector('.decrease-button');
        const increaseButton = productItem.querySelector('.increase-button');
        const inputs = document.querySelectorAll('input[id^="product-"]');
        
        let currentQuantity = parseInt(quantityDisplay.textContent);
        
        function formatPrice(price) {
            // Убираем пробелы и любые символы, кроме цифр, точки и минуса
            const cleanPrice = price.replace(/\s+/g, '').replace(',', '.');  
            const number = parseFloat(cleanPrice);
        
            // Если значение не число, возвращаем как есть
            if (isNaN(number)) return price;
        
            // Проверяем, является ли число целым
            const hasDecimal = !Number.isInteger(number);
        
            // Форматируем число с разделением тысяч пробелами
            return number.toLocaleString('ru-RU', {
                minimumFractionDigits: hasDecimal ? 2 : 0,
                maximumFractionDigits: 2
            });
        }
        
        // Функция обновления количества для конкретного товара
        function updateQuantity(newQuantity, action = '') {
            fetch('/cart/cart_holder/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ 
                    product_id: productId,
                    quantity: newQuantity, 
                    action: action
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    currentQuantity = newQuantity;
                    quantityDisplay.textContent = currentQuantity;
                    
                    // Обновляем цену товара
                    const priceElement = productItem.querySelector('.product-price');
                    const formattedPrice = formatPrice(data.price);
                    priceElement.textContent = formattedPrice + ' ₽';
                    
                    const summaryItem = document.querySelector(`.item-list-detail[data-product-id="${productId}"]`);
                    if (summaryItem) {
                        const quantityElement = summaryItem.querySelector('.item-quantity');
                        if (quantityElement) {
                            quantityElement.textContent = currentQuantity;
                        }
                    }

                    updateTotalPrice(data.total_price);
                    // Обновляем отображение в summary
                    
                    // Управление состоянием кнопок
                    decreaseButton.disabled = currentQuantity <= MIN_QUANTITY;
                    increaseButton.disabled = currentQuantity >= MAX_QUANTITY;
        
                    // Если количество стало 0, удаляем элемент
                    if (currentQuantity === 0) {
                        productItem.remove();
                        removeFromSummary(productId);
                    }
                }
            })
            .catch(error => {
                console.error('Ошибка при обновлении количества:', error);
            });
        }

        // Обработчик уменьшения количества
        decreaseButton.addEventListener('click', () => {
            if (currentQuantity > MIN_QUANTITY) {
                updateQuantity(currentQuantity - 1, 'decrease');
            }
        });

        // Обработчик увеличения количества
        increaseButton.addEventListener('click', () => {
            if (currentQuantity < MAX_QUANTITY) {
                updateQuantity(currentQuantity + 1, 'increase');
            }
        });

        // Начальное состояние кнопок
        decreaseButton.disabled = currentQuantity <= MIN_QUANTITY;
        increaseButton.disabled = currentQuantity >= MAX_QUANTITY;
    });
});

// Функция форматирования цены
function formatPrice(price) {
    // Преобразуем в строку, если передано число
    if (typeof price !== 'string') {
        price = String(price);
    }

    // Убираем все символы, кроме цифр, точки и запятой
    price = price.replace(/[^\d.,]/g, '').replace(',', '.');

    // Преобразуем в число
    const number = parseFloat(price);

    // Если не удалось преобразовать в число, возвращаем исходное значение
    if (isNaN(number)) return price;

    // Форматируем число с разделением тысяч
    return number.toLocaleString('ru-RU', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });
}

// Функция обновления общей стоимости
function updateTotalPrice(totalPrice) {
    const totalPriceElement = document.querySelector('.total-amount');
    if (totalPriceElement) {
        totalPriceElement.textContent = `${totalPrice} ₽`;
    }
}

// Функция удаления товара из summary
function removeFromSummary(productId) {
    const itemDetail = document.querySelector(`.item-list-detail[data-product-id="${productId}"]`);
    if (itemDetail) {
        itemDetail.remove();
    }
}

// Функция удаления товара
function removeProduct(productId){
    fetch('/cart/cart_holder/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ 
            product_id: productId,
            quantity: 0,
            action: 'remove'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Удаляем элемент товара
            const productItem = document.querySelector(`.product-item[data-product-id="${productId}"]`);
            if (productItem) {
                productItem.remove();
            }
            // Удаляем из summary
            removeFromSummary(productId);
            // Обновляем общую стоимость
            updateTotalPrice(data.total_price);
        }
    })
    .catch(error => {
        console.error('Ошибка при удалении товара:', error);
    });
}

function toggleSelection(element) {
    element.classList.toggle('active');
    element.classList.toggle('inactive');
}


function getCsrfToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}