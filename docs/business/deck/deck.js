const slides = Array.from(document.querySelectorAll(".slide"));
const prevButton = document.getElementById("prev-btn");
const nextButton = document.getElementById("next-btn");
const slideLabel = document.getElementById("slide-label");
const progressFill = document.getElementById("progress-fill");

let currentIndex = 0;

function getSlideFromHash() {
  const hash = window.location.hash.replace(/^#slide-/, "");
  const parsed = Number.parseInt(hash, 10);
  if (Number.isNaN(parsed)) {
    return 0;
  }
  return Math.min(Math.max(parsed - 1, 0), slides.length - 1);
}

function updateChrome() {
  const slideNumber = String(currentIndex + 1).padStart(2, "0");
  const totalSlides = String(slides.length).padStart(2, "0");
  const title = slides[currentIndex]?.dataset.title ?? "";
  const progress = ((currentIndex + 1) / slides.length) * 100;

  slideLabel.textContent = `${slideNumber} / ${totalSlides}  ${title}`;
  progressFill.style.width = `${progress}%`;
  prevButton.disabled = currentIndex === 0;
  nextButton.disabled = currentIndex === slides.length - 1;
  document.title = `RouteScout Founder Deck - ${title}`;
}

function showSlide(index, { updateHash = true } = {}) {
  currentIndex = Math.min(Math.max(index, 0), slides.length - 1);

  slides.forEach((slide, slideIndex) => {
    const isActive = slideIndex === currentIndex;
    slide.classList.toggle("is-active", isActive);
    slide.setAttribute("aria-hidden", String(!isActive));
  });

  if (updateHash) {
    window.location.hash = `slide-${currentIndex + 1}`;
  }

  updateChrome();
}

function nextSlide() {
  showSlide(currentIndex + 1);
}

function previousSlide() {
  showSlide(currentIndex - 1);
}

prevButton.addEventListener("click", previousSlide);
nextButton.addEventListener("click", nextSlide);

document.addEventListener("keydown", (event) => {
  const blocked = event.metaKey || event.ctrlKey || event.altKey;
  if (blocked) {
    return;
  }

  switch (event.key) {
    case "ArrowRight":
    case "PageDown":
    case " ":
    case "Enter":
      event.preventDefault();
      nextSlide();
      break;
    case "ArrowLeft":
    case "PageUp":
    case "Backspace":
      event.preventDefault();
      previousSlide();
      break;
    case "Home":
      event.preventDefault();
      showSlide(0);
      break;
    case "End":
      event.preventDefault();
      showSlide(slides.length - 1);
      break;
    default:
      break;
  }
});

window.addEventListener("hashchange", () => {
  showSlide(getSlideFromHash(), { updateHash: false });
});

showSlide(getSlideFromHash(), { updateHash: false });
