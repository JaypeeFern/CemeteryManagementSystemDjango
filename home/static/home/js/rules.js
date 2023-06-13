function success() {
    if(document.getElementById("name").value==="") { 
             document.getElementById('button').disabled = true; 
         } else if(document.getElementById("username_register").value==="") { 
             document.getElementById('button').disabled = true;
         } else if(document.getElementById("password1").value==="") { 
             document.getElementById('button').disabled = true;
         } else if(document.getElementById("password2").value==="") { 
             document.getElementById('button').disabled = true;
         } else { 
             document.getElementById('button').disabled = false; 
         }
     }
   
     var input = document.querySelectorAll('.enterevent');
     for (var i = 0; i < input.length; i++) {
         input[i].addEventListener('keypress', function(event) {
             if (event.key === 'Enter'){
                 event.preventDefault();
                 document.getElementById('button').click();
             }
         });
     }