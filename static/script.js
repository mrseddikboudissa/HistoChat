let savedpasttext = []; // Variable to store the message
let savedpastresponse = []; // Variable to store the message

// Section: get the Id of the talking container
const messagesContainer = document.getElementById('messages-container');
const messageForm = document.getElementById('message-form');
const messageInput = document.getElementById('message-input');
//

// Get the image-related elements
const imageupload =document.getElementById('imageUpload');
const previewContained = document.getElementById('previewContainer');
const previewimage = document.getElementById('previewImage');
const removeImageBtn = document.getElementById('removeImageBtn');

// Get the document-related elements
const documentupload = document.getElementById('documentUpload');
const pdfStatusMessage = document.createElement('div');
pdfStatusMessage.id = 'pdf-status';
messagesContainer.appendChild(pdfStatusMessage);


//Section: function to creat the dialogue window
const addMessage = (message, role, imgSrc , uploadedImage=null) => { //This is the function that renders a message bubble in the chat.
//  It takes 3 things — the text, the role (user/aibot/error), 
// and an avatar image path and the uploaded image.
//  It creates the div, adds the avatar and text, and appends it to the chat container.
  
// creat elements in the dialogue window
// here we are creating extra html elements using JavaScript to build the structure of the message bubble. We create a div for the message, a paragraph for the text, and an img for the avatar. We set the class of the message div based on the role (user/aibot/error) to style it differently. We also set the source of the avatar image to the provided imgSrc.
  const messageElement = document.createElement('div');
  const textElement = document.createElement('p');
  messageElement.className = `message ${role}`;
  const imgElement = document.createElement('img');
  imgElement.src = `${imgSrc}`;
  // append the image and message to the message element
  messageElement.appendChild(imgElement);


  if (uploadedImage) {
    const uploadedImgElement = document.createElement('img');

    uploadedImgElement.src = uploadedImage;
    uploadedImgElement.className = 'uploaded-image';
    messageElement.appendChild(uploadedImgElement);
      // Force text to appear below the image
  const clearDiv = document.createElement('div');
  clearDiv.style.clear = 'both';
  messageElement.appendChild(clearDiv);
  }

  textElement.innerText = message;
  messageElement.appendChild(textElement);
  messagesContainer.appendChild(messageElement);
  // creat the ending of the message
  var clearDiv = document.createElement("div");
  clearDiv.style.clear = "both";
  messagesContainer.appendChild(clearDiv);
};
//


//Section: Calling the model
const sendMessage = async (message) => {  // this does 4 things : 

//shows the user's message, 
// shows the loading animation, 
// sends the text to Flask via fetch(), 
// then removes the loading animation 
// and shows the bot's response.

   const imagefile = imageupload.files[0]; // we get the selected image file from the file input element. This is the image that the 
   let imagedataurl = null; // we initialize a variable to store the data URL of the image. A data URL is a way to represent the image as a string that can be used as the source of an img element. 

   if (imagefile){
    imagedataurl = previewImage.src; // we create a FileReader object to read the contents of the image file.
   }

  // addMessage(message, 'user','user.jpeg');
  addMessage(message, 'user', '../static/profile.png', imagedataurl);
   
    // Clear the image preview after sending
  imageUpload.value = '';
  previewImage.src = '';
  previewContainer.classList.remove('active');

  // Loading animation
  const loadingElement = document.createElement('div');
  const loadingtextElement = document.createElement('p');
  loadingElement.className = `loading-animation`;
  loadingtextElement.className = `loading-text`;
  loadingtextElement.innerText = 'Loading....Please wait';
  messagesContainer.appendChild(loadingElement);
  messagesContainer.appendChild(loadingtextElement);



//We need to use FormData instead, which can carry both text and files together.


async function makePostRequest(msg,imageFile) {
    const url = 'http://127.0.0.1:5000/chatbot';  // Make a POST request to this url


    const formData = new FormData(); // Create a new FormData object to hold the data we want to send to the backend. FormData is a special type of object that can hold both text and files, making it ideal for our use case where we want to send a message along with an optional image.
    formData.append('prompt',msg); // We append the message text to the FormData object with the key 'prompt'. This is how we include the user's message in the data we send to the backend.
    if (imageFile) {
      formData.append('image', imageFile);
    }

  
    try {
      
      
      //🟢 STEP 2 — Send request to backend
      //fetch() = HTTP request to backend and wait for the response

      const response = await fetch(url, {
        method: 'POST',
      // No 'Content-Type' header here — browser sets it automatically for FormData

        body:formData
      });
      
//🟡 STEP 10 — Frontend receives response

const data = await response.text(); //Here we wait for the answer from the backend and we store it in the variable data
      // Handle the response data here
      console.log(data);
      return data;
    } catch (error) {
      // Handle any errors that occurred during the request
      console.error('Error:', error);
      return error
    }
  }
  


  var res = await makePostRequest(message,imagefile);
  
  data = {"response": res};
  
  // Deleting the loading animation
  const loadanimation = document.querySelector('.loading-animation');
  const loadtxt = document.querySelector('.loading-text');
  loadanimation.remove();
  loadtxt.remove();

  if (data.error) {
    // Handle the error here
    const errorMessage = JSON.stringify(data);
    // addMessage(errorMessage, 'error','Error.png');
    addMessage(errorMessage, 'error','../static/Error.png');
  } else {
    // Process the normal response here
    const responseMessage = data['response'];
    // addMessage(responseMessage, 'aibot','Bot_logo.png');

    //👉 🟡STEP 11 Displays message in UI
    addMessage(responseMessage, 'aibot','../static/Bot_logo.png');
  }
  
  //!!!!! code to  save the content in history
  //
};
//

//Section: Button to submit to the model and get the response

// User writes a message (Frontend)
 //🟢 STEP 1 — Write the message
messageForm.addEventListener('submit', async (event) => {

  
  event.preventDefault();
  const message = messageInput.value.trim();
  const hasImage = imageUpload.files[0];
  const hasPdf = documentupload.files[0];

  if (message !=='' || imageupload.files.length > 0) { // we check if the message is not empty or if there is an image selected. This ensures that we only send a request to the backend if there is something to send (either text or an image).
    messageInput.value = '';
  
          // If a PDF has been uploaded, use RAG mode
        if (hasPdf && message !== '') {
            console.log("Sending message with PDF...");
            await sendMessageWithPdf(message);
        } else {
            console.log("Sending message without PDF...");
            await sendMessage(message);
        }

  
  }
});


imageupload.addEventListener('change',() => { // the change happens when the user selects an image from their device. We read that image and display it in the preview container.
 const file = imageupload.files[0]; //The <input type="file"> stores files inside: it an array that why we use [0] to get the first file. 
 if(file){
  const reader = new FileReader(); //FileReader is a built-in JavaScript class that allows us to read the contents of files (like images) on the client side. We create an instance of it to read the selected image file.
  //JavaScript cannot directly access local files for security.Instead we use FileReader to safely read the file.

  reader.onload = (e) => { //on load means when file finishes loading into the reader, we execute this function. The event object e contains the result of reading the file.
    previewimage.src = e.target.result;
    previewContained.classList.add('active'); // he we add active class of css to preview the image 
  };
  reader.readAsDataURL(file);
  }});

  removeImageBtn.addEventListener('click',() => { // this is the function that removes the previewed image when the user clicks the remove button.

    imageupload.value = ''; // we clear the file input so that it no longer holds the selected image.
    previewimage.src = ''; // we clear the src of the preview image to remove it from view.
    previewContained.classList.remove('active'); // we remove the active class to hide the preview container again.

  });




documentupload.addEventListener('change', async () => {
    const file = documentupload.files[0];
    if (!file) return;

    // Show processing message in chat
    addMessage(`Uploading document: ${file.name}...`, 'aibot', '../static/Bot_logo.png');

    const formData = new FormData();
    formData.append('pdf', file);

    try {
        const response = await fetch('http://127.0.0.1:5000/upload_pdf', {
            method: 'POST',
            body: formData
        });

        const result = await response.text();
        addMessage(result, 'aibot', '../static/Bot_logo.png');

    } catch (error) {
        addMessage('Error uploading document. Please try again.', 'error', '../static/Error.png');
        console.error('PDF upload error:', error);
    }
});


const sendMessageWithPdf = async (message) => {
    addMessage(message, 'user', '../static/profile.png');
    
    // Show loading animation
    const loadingElement = document.createElement('div');
    const loadingTextElement = document.createElement('p');
    loadingElement.className = 'loading-animation';
    loadingTextElement.className = 'loading-text';
    loadingTextElement.innerText = 'Searching document...';
    messagesContainer.appendChild(loadingElement);
    messagesContainer.appendChild(loadingTextElement);

    try {
        const formData = new FormData();
        formData.append('prompt', message);

        const response = await fetch('http://127.0.0.1:5000/ask_pdf', {
            method: 'POST',
            body: formData
        });

        const data = await response.text();

        // Remove loading animation
        loadingElement.remove();
        loadingTextElement.remove();

        addMessage(data, 'aibot', '../static/Bot_logo.png');

    } catch (error) {
        loadingElement.remove();
        loadingTextElement.remove();
        addMessage('Error querying document.', 'error', '../static/Error.png');
        console.error('PDF query error:', error);
    }
};