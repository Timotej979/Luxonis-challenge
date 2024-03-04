// index.js
document.addEventListener('DOMContentLoaded', fetchApartments);

const startCrawlerEndpoint = 'http://127.0.0.1:8080/scraper-api/v1/start-scraper';
const clearFlatsEndpoint = 'http://127.0.0.1:8080/scraper-api/v1/clear-flats';
const getFlatItemsEndpoint = 'http://127.0.0.1:8080/scraper-api/v1/flat-items';

function startCrawler() {
    const itemCount = document.getElementById('itemCount').value;

    fetch(startCrawlerEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ item_count: itemCount }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to start the crawler');
        }
        fetchApartments();
    })
    .catch(error => {
        console.error('Error starting the crawler:', error);
    });
}

function deleteAllApartments() {
    fetch(clearFlatsEndpoint, {
        method: 'DELETE',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to delete all apartments');
        }
        // Clear the apartment list after deletion
        const apartmentList = document.getElementById('apartment-list');
        apartmentList.innerHTML = '';
    })
    .catch(error => {
        console.error('Error deleting all apartments:', error);
    });
}

async function fetchApartments() {
    try {
        const response = await fetch(getFlatItemsEndpoint);
        const data = await response.json();
        displayApartments(data);
    } catch (error) {
        console.error('Error fetching apartment data:', error);
    }
}

function displayApartments(apartments) {
    const apartmentList = document.getElementById('apartment-list');

    apartments.forEach(apartment => {
        const listItem = document.createElement('li');
        listItem.className = 'apartment-item';

        const title = document.createElement('h2');
        title.textContent = apartment.title;

        const image = document.createElement('img');
        image.src = apartment.image;
        image.alt = apartment.title;

        listItem.appendChild(title);
        listItem.appendChild(image);
        apartmentList.appendChild(listItem);
    });
}
