

let currentPage = 0;

const pageNumber = document.querySelector('.page-number');
const contentPane = document.querySelector('.content-pane');
const previousBtn = document.querySelector('.previous-btn');
const nextBtn = document.querySelector('.next-btn');
const doneBtn = document.querySelector('.done-btn');

function updateContent() {
    pageNumber.textContent = `Page ${currentPage + 1} of ${prompts.length}`;

    previousBtn.style.display = currentPage === 0 ? 'none' : 'inline-block';
    nextBtn.style.display = currentPage === prompts.length - 1 ? 'none' : 'inline-block';
    doneBtn.style.display = currentPage === prompts.length - 1 ? 'inline-block' : 'none';

    if (prompts[currentPage][0]==1)
    {
        document.getElementById("showtranslation").style.display = "";
        document.getElementById("audioControl").style.display = ""
        document.getElementById("audioControl").src = "/lesson1/" + prompts[currentPage][1];
    document.getElementById("englishText").innerText = prompts[currentPage][2];
    document.getElementById("spanishText").innerText = prompts[currentPage][3];
    document.getElementById("spanishText").style.visibility = "hidden";
      document.getElementById("audioControl").play();



    }
    else if (prompts[currentPage][0]==0)
    {
        document.getElementById("englishText").innerText = prompts[currentPage][1];
        document.getElementById("audioControl").style.display = "none";
        document.getElementById("showtranslation").style.display = "none";

    }
    else
    {
        document.getElementById("englishText").innerText = "Error, invalid prompt type!";

    }

}

previousBtn.addEventListener('click', () => {
    currentPage--;
    updateContent();
});

nextBtn.addEventListener('click', () => {
    currentPage++;
    updateContent();
});

// doneBtn.addEventListener('click', () => {
//     window.location.href = '/';
// });

// cancelBtn.addEventListener('click', () => {
//     window.location.href = '/';
// });

updateContent();

function preloadAudio() {
  prompts.forEach(prompt => {
      if (prompt[0] == 1){
    let audio = new Audio("/lesson1/" + prompt[1]);
    audio.preload = "auto";
    prompt.push(audio);}
  });
}

function showTranslation() {
  var elem = document.getElementById("spanishText");
  if (elem.style.visibility === "hidden") {
    elem.style.visibility = "visible";
  } else {
    elem.style.visibility = "hidden";
  }
}

window.onload = function() {
  preloadAudio();
  updateContent();
}


