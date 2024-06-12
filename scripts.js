document.getElementById('fetch-drugs').addEventListener('click', function() {
    fetch('/stocked-drugs')
        .then(response => response.json())
        .then(data => {
            const drugList = document.getElementById('drug-list');
            drugList.innerHTML = '';
            data.forEach(drug => {
                const listItem = document.createElement('li');
                listItem.textContent = `${drug['Drug Name']} - ${drug['Stock Quantity']} in stock`;
                drugList.appendChild(listItem);
            });
        });
});
