let flashcards = [];
let index = 0;
let isFlipped = false;
let requestedNumCards = 5;  // store requested number separately

function updateCard() {
  // Show front or back of current card
  document.getElementById("cardContent").textContent = isFlipped ? flashcards[index].a : flashcards[index].q;

  // Show requested number in UI (even if fewer cards received)
  document.getElementById("cardCounter").textContent = `${index + 1} / ${flashcards.length}`;

}

function flipCard() {
  isFlipped = !isFlipped;
  updateCard();
}

function nextCard() {
  if (index < flashcards.length - 1) {
    index++;
    isFlipped = false;
    updateCard();
  } else {
    alert(`Only ${flashcards.length} flashcards were generated. Can't go further.`);
  }
}

function prevCard() {
  if (index > 0) {
    index--;
    isFlipped = false;
    updateCard();
  }
}

async function generateFlashcards() {
  const input = document.getElementById("pdfInput");
  const file = input.files[0];
  requestedNumCards = parseInt(document.getElementById("numCards").value);

  if (!file) {
    alert("Please upload a PDF.");
    return;
  }

  const loading = document.getElementById("loadingMessage");
  loading.style.display = "block"; // Show loading

  const formData = new FormData();
  formData.append("file", file);
  formData.append("num", requestedNumCards);

  try {
    const response = await fetch("https://studycard-bv10.onrender.com/upload_pdf", {
      method: "POST",
      body: formData
    });

    const data = await response.json();
    loading.style.display = "none"; // Hide loading

    if (data.flashcards) {
      // Limit to requested number just in case backend sends more
      flashcards = data.flashcards.slice(0, requestedNumCards);
      index = 0;
      isFlipped = false;
      updateCard();
    } else {
      alert("Error: " + JSON.stringify(data));
    }
  } catch (err) {
    console.error(err);
    alert("Failed to generate flashcards. See console for details.");
    loading.style.display = "none"; // Hide on error
  }
}
