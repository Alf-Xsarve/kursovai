
const visitDateInput = document.getElementById("visit-date");
const adultsInput = document.getElementById("adults");
const childrenInput = document.getElementById("children");
const totalPriceElement = document.getElementById("total-price");
const hiddenTotalPriceInput = document.getElementById("hidden-total-price");
const bookingButton = document.querySelector(".booking-form button");
const notificationElement = document.getElementById("notification");

// Проверяем существование элементов
if (!visitDateInput || !adultsInput || !childrenInput || !totalPriceElement || !bookingButton || !notificationElement) {
    console.error("Один или несколько элементов формы не найдены.");
    return;
}

// Цены билетов
const ticketPrices = {
    adult: 1000,
    child: 500,
};

// Функция обновления цены
function updatePrice() {
    const adults = parseInt(adultsInput.value, 10);
    const children = parseInt(childrenInput.value, 10);

    if (isNaN(adults) || adults < 1) {
        adultsInput.value = 1; // Минимальное значение
    }
    if (isNaN(children) || children < 1) {
        childrenInput.value = 1; // Минимальное значение
    }

    // Вычисляем итоговую стоимость
    const totalPrice = (ticketPrices.adult * adults) + (ticketPrices.child * children);

    // Обновляем отображение итоговой стоимости на странице
    totalPriceElement.textContent = totalPrice.toLocaleString("ru-RU") + " сом";

    // Обновляем скрытое поле для отправки данных
    hiddenTotalPriceInput.value = totalPrice;
}

// Обновляем цену при изменении количества взрослых и детей
adultsInput.addEventListener("input", updatePrice);
childrenInput.addEventListener("input", updatePrice);
visitDateInput.addEventListener("change", updatePrice);

// Изначальное обновление цены
updatePrice();

// Обработчик на кнопку бронирования
bookingButton.addEventListener("click", function (event) {
    event.preventDefault(); // Предотвращаем отправку формы

    // Показываем уведомление
    notificationElement.style.display = "block";

    // Перенаправление на главную страницу через 2 секунды
    setTimeout(function () {
        window.location.href = "index.html"; // Путь к главной странице
    }, 2000);
});