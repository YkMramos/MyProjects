// Инициализация Telegram WebApp
const tg = window.Telegram.WebApp;
tg.setHeaderColor('#000');
tg.ready();
tg.expand();  // Расширяем на весь экран
tg.disableVerticalSwipes();
tg.BackButton.hide();

// Обработка карточек товаров
document.addEventListener('DOMContentLoaded', function() {
    // Обработчики для карточек товаров
    document.querySelectorAll('.product-card').forEach(card => {
        const MAX_QUANTITY = 15;
        
        const productId = card.dataset.productId;
        const addToCartBtn = document.getElementById(`add-to-cart-btn-${productId}`);
        const quantityDisplay = document.getElementById(`quantity-display-${productId}`);
        const decreaseButton = document.getElementById(`decrease-button-${productId}`);
        const increaseButton = document.getElementById(`increase-button-${productId}`);
        const quantityControl = card.querySelector('.quantity-control');
        
        let currentQuantity = parseInt(quantityDisplay.textContent, 10) || 0;
        
        function initializeUIState() {
            if (currentQuantity > 0) {
                addToCartBtn.style.display = 'none';
                quantityControl.style.display = 'flex';
                quantityDisplay.textContent = currentQuantity;
                increaseButton.disabled = currentQuantity >= MAX_QUANTITY;
            } else {
                addToCartBtn.style.display = 'block';
                quantityControl.style.display = 'none';
            }
        }
        
        function updateQuantity(newQuantity, action = '') {
            fetch(`/cart/update_product_quantity/${productId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ 
                    quantity: newQuantity, 
                    action: action,
                    options: {
                        memory: localStorage.getItem('selected_Память'),
                        color: localStorage.getItem('selected_Цвет'),
                        sim: localStorage.getItem('selected_SIM-карта')
                    }
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    currentQuantity = newQuantity;
                    quantityDisplay.textContent = currentQuantity;
                    document.querySelector('.cart-count').textContent = data.total_count;
                   
                    initializeUIState();
                }
            })
            .catch(error => {
                console.error('Ошибка при обновлении количества:', error);
            });
        }
    
        addToCartBtn.addEventListener('click', () => {
            if (currentQuantity === 0) {
                updateQuantity(1, 'add_to_cart');
            }
        });
    
        decreaseButton.addEventListener('click', () => {
            if (currentQuantity === 1) {
                updateQuantity(0, 'remove');
            } else if (currentQuantity > 1) {
                updateQuantity(currentQuantity - 1, 'decrease');
            }
        });
    
        increaseButton.addEventListener('click', () => {
            if (currentQuantity < MAX_QUANTITY) {
                updateQuantity(currentQuantity + 1, 'increase');
            }
        });
    
        // Вызываем initializeUIState при загрузке страницы
        initializeUIState();
    });

    // Обработчики для сортировки и фильтрации
    const sortMenu = document.querySelector('.sort-menu');
    const filterMenu = document.querySelector('.filter-menu');

    // Обработчики для опций сортировки
    if (document.querySelectorAll('.sort-option').length > 0) {
        document.querySelectorAll('.sort-option').forEach(option => {
            option.addEventListener('click', function(e) {
                e.stopPropagation();
                const sortType = this.dataset.sort;
                // Здесь можно добавить AJAX-запрос к Django view
                fetch(`/sort/?type=${sortType}`)
                    .then(response => response.json())
                    .then(data => {
                        // Обновление данных на странице
                        console.log('Сортировка:', sortType);
                    });
                if (sortMenu) sortMenu.style.display = 'none';
            });
        });
    }

    // Закрытие меню при клике вне его
    document.addEventListener('click', function(e) {
        if ((!e.target.closest('.sort-container') && sortMenu) && 
            (!e.target.closest('.filter-container') && filterMenu)) {
            if (sortMenu) sortMenu.style.display = 'none';
            if (filterMenu) filterMenu.style.display = 'none';
        }
    });

    // Обработка изменений фильтров
    let timeout = null;
    const filters = document.querySelectorAll('#price-min, #price-max, #memory');
    
    if (filters.length > 0) {
        filters.forEach(filter => {
            filter.addEventListener('change', function() {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    const formData = new FormData();
                    formData.append('price_min', document.getElementById('price-min').value);
                    formData.append('price_max', document.getElementById('price-max').value);
                    formData.append('memory', document.getElementById('memory').value);
                    
                    // Здесь можно добавить AJAX-запрос к Django view
                    fetch('/filter/', {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': getCsrfToken()
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        // Обновление данных на странице
                        console.log('Фильтры применены:', data);
                    });
                }, 500);
            });
        });
    }
});

// Функция для получения CSRF-токена
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