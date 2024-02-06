const user_id =3;  // Replace with actual user ID
const userId = 1;
const postId = 11;
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhdmluYXNoIiwiZXhwIjoxNzA1OTQwNjcxfQ.WZD2JnWigD0bbAuGXOz3QMfk167yH0XTa5iMW5qndqo";
// fetch(`http://localhost:8000/notes/create`, {  
//     method: 'POST',
//     headers: {
//         'Authorization': `Bearer ${token}`,  
//         'Content-Type': 'application/json' 
//     },
//     body: JSON.stringify({  
//         "title": "Test Db 2",
//         "content": "Testing db whether its adding or not",
//         "user_id": userId  
//     })
// })
// .then(response => response.json())
// .then(data => console.log(data))
// .catch(error => console.error('Error:', error));
fetch(`http://localhost:8000/notes/update`, {  
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,  
        'Content-Type': 'application/json' 
    },
    body: JSON.stringify({  
        "title": "Updated texxt",
        "content": "Testing db update whether its adding or not",
        "post_id": 2,
    })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));

// fetch(`http://localhost:8000/user/${userId}`, {
//     method: 'DELETE',
//     headers: {
//         'Authorization': `Bearer ${token}`
//     }
// })
// .then(response => response.json())
// .then(data => console.log(data))
// .catch(error => console.error('Error:', error));

// fetch(`http://localhost:8000/notes/delete/${postId}`, {
//     method: 'DELETE',
//     headers: {
//         'Authorization': `Bearer ${token}`
//     }
// })
// .then(response => response.json())
// .then(data => console.log(data))
// .catch(error => console.error('Error:', error));


// fetch(`http://localhost:8000/users/${user_id}/notes`, {
//     method: 'GET',
//     headers: {
//         'Authorization': `Bearer ${token}`
//     }
// })
// .then(response => response.json())
// .then(data => console.log(data))
// .catch(error => console.error('Error:', error));
