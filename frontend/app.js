const API_URL = "https://1z05rkzzd2.execute-api.eu-north-1.amazonaws.com/today";

function renderList(elementId, items) {
  const element = document.getElementById(elementId);
  element.innerHTML = "";

  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = "Inga hittades för idag";
    li.className = "empty";
    element.appendChild(li);
    return;
  }

  for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item;
    element.appendChild(li);
  }
}

async function loadToday() {
  const dateElement = document.getElementById("date");
  const errorElement = document.getElementById("error");

  try {
    const response = await fetch(API_URL);

    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }

    const data = await response.json();

    dateElement.textContent = data.date;

    renderList("holidays", data.sweden.holidays);
    renderList("halfDays", data.sweden.halfDays);
    renderList("bridgeDays", data.sweden.bridgeDays);
    renderList("finlandHolidays", data.finland.holidays);
  } catch (error) {
    dateElement.textContent = "Could not load data";
    errorElement.style.display = "block";
    errorElement.textContent = error.message;
  }
}

loadToday();