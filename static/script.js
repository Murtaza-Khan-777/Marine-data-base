let currentindex = 0;

document.addEventListener("DOMContentLoaded", () => {
    setTimeout(() => {
        document.getElementById('text-content').classList.remove('opacity-0', 'translate-y-8');
        document.getElementById('image-container').classList.remove('opacity-0');
    }, 100);

    let menu_items = document.querySelectorAll('.specie-menu-item');
    for (let i = 0; i < menu_items.length; i++) {
        menu_items[i].addEventListener('click', () => {
            let target_name = menu_items[i].getAttribute('data-name');
            let target_index = -1;
            
            for (let k = 0; k < db_data.length; k++) {
                if (db_data[k].name === target_name) {
                    target_index = k;
                }
            }
            
            if (target_index !== -1) {
                changespecie(target_index);
            }
        });
    }

    let search_input = document.getElementById('search-input');
    let search_results = document.getElementById('search-results');

    search_input.addEventListener('input', (e) => {
        let query = e.target.value.toLowerCase();
        search_results.innerHTML = '';
        
        if (query === '') {
            search_results.classList.add('hidden');
            search_results.classList.remove('flex');
        } else {
            search_results.classList.remove('hidden');
            search_results.classList.add('flex');
            
            let match_count = 0;
            for (let j = 0; j < db_data.length; j++) {
                let specie_name = db_data[j].name.toLowerCase();
                
                if (specie_name.includes(query)) {
                    match_count++;
                    let li = document.createElement('li');
                    li.className = "px-4 py-3 hover:bg-cyan-900/40 cursor-pointer text-sm text-gray-300 hover:text-white border-b border-white/5 last:border-none transition-colors";
                    li.textContent = db_data[j].name.toUpperCase();
                    
                    li.onclick = () => {
                        changespecie(j);
                        search_input.value = '';
                        search_results.classList.add('hidden');
                        search_results.classList.remove('flex');
                    };
                    
                    search_results.appendChild(li);
                }
            }
            
            if (match_count === 0) {
                let li = document.createElement('li');
                li.className = "px-4 py-3 text-sm text-white/40 italic";
                li.textContent = "No species found";
                search_results.appendChild(li);
            }
        }
    });
});

function togglesidebar() {
    let sidebar = document.getElementById('sidebar');
    if (sidebar.classList.contains('translate-x-0')) {
        sidebar.classList.remove('translate-x-0', 'opacity-100');
        sidebar.classList.add('translate-x-12', 'opacity-0', 'pointer-events-none');
    } else {
        sidebar.classList.remove('translate-x-12', 'opacity-0', 'pointer-events-none');
        sidebar.classList.add('translate-x-0', 'opacity-100');
    }
}

function changespecie(index) {
    if (index === currentindex) {
        return;
    }
    if (index >= db_data.length) {
        return;
    }
    
    let data = db_data[index];
    let text_content = document.getElementById('text-content');
    let image_container = document.getElementById('image-container');
    let bg_image = document.getElementById('bg-image');
    
    text_content.classList.add('opacity-0', 'translate-y-4');
    image_container.classList.add('opacity-0');
    
    // Fade out background image properly from 50 to 0
    bg_image.classList.remove('opacity-50');
    bg_image.classList.add('opacity-0');

    setTimeout(() => {
        let habitat_title_el = document.getElementById('habitat-title');
        habitat_title_el.textContent = data.habitat.toUpperCase();

        let title_el = document.getElementById('specie-title');
        title_el.textContent = data.name;
        title_el.className = `text-7xl md:text-8xl font-bold uppercase tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r ${data.gradient} drop-shadow-[0_0_15px_${data.shadow}]`;
        
        document.getElementById('specie-desc').textContent = data.desc;
        
        let main_img_el = document.getElementById('main-image');
        main_img_el.src = data.img;
        main_img_el.className = `w-full h-full object-cover rounded-full filter ${data.glowclass} float-animation mix-blend-screen`;
        
        bg_image.src = data.bgimg;
        // Notice we maintain opacity-80 here on the overlay div so it never totally blacks out the image
        document.getElementById('bg-overlay').className = `absolute inset-0 bg-gradient-to-br ${data.overlaygradient} opacity-80 transition-colors duration-1000`;

        text_content.classList.remove('opacity-0', 'translate-y-4');
        image_container.classList.remove('opacity-0');
        
        // Fade in background image back to 50
        bg_image.classList.remove('opacity-0');
        bg_image.classList.add('opacity-50');
        
        currentindex = index;
    }, 500);
}