
// Получаем элементы формы
const adultsInput = document.getElementById("adults");
const childrenInput = document.getElementById("children");
const totalPriceElement = document.getElementById("total-price");
if (!adultsInput || !childrenInput || !totalPriceElement) {
    console.error("Один или несколько элементов формы не найдены.");
    return;
}
const ticketPrices = {
    adult: 1000,
    child: 500
};
function updatePrice() {
    const adultsCount = parseInt(adultsInput.value, 10) || 0;
    const childrenCount = parseInt(childrenInput.value, 10) || 0;
    const totalPrice = (adultsCount * ticketPrices.adult) + (childrenCount * ticketPrices.child);
    totalPriceElement.textContent = totalPrice.toLocaleString("ru-RU") + " сом";
    const hiddenTotalPrice = document.getElementById("hidden-total-price");
    if (hiddenTotalPrice) {
        hiddenTotalPrice.value = totalPrice;
    }
}
adultsInput.addEventListener("input", updatePrice);
childrenInput.addEventListener("input", updatePrice);
updatePrice();