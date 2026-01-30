const AFWAN_GLOBAL_THEME = {
    greyColor: '#f8f9fa',
    primaryColor: '#007bff'
};

//${AFWAN_GLOBAL_THEME.greyColor}

class SmartFormEngine {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    render(fields, buttonText = "Submit Form") {
        let html = "";

        // 1. Forms input
        //html += '<div class="row">'; 
        html += '<div class="column">'; 
        html += fields.map((f, i) => this.createSmartField(f, i+1)).join('');
        html += '</div>';

        // html += <div class="fs-6"><i>*Video must atleast 1 min</i></div>;

        //2. Button
        html += `
        <div class="col-12 mt-2">
            <button type="submit" id="submit-btn" class="btn btn-secondary" style="color:white;">
                ${buttonText}
            </button>
        </div>`;
        
        this.container.innerHTML = html;
        this.initLogic();
    }

    // This is the "Master Template" that handles everything
    createSmartField(config, index) {

        //File type
        if (config.type === 'file') {
            return this.createUploadTemplate(config, index);
        }

        // 1. Logic for Styles & Keywords
        let inputClasses = ['form-control']; 
        let styleAttr = '';
        let required = "";
        let requiredTag = "";

        if (config.transform) {
            if (config.transform.includes('uppercase')) inputClasses.push('force-upper');
            if (config.transform.includes('italic'))    inputClasses.push('fst-italic'); 
            if (config.transform.includes('grey'))      styleAttr += 'background-color: #f8f9fa;'; 
            if (config.transform.includes('required'))  required = "required"; 
            if (config.transform.includes('required'))  requiredTag = <span style="color:red;">*</span>; 
        }

        // 2. Return the HTML with both Grid (col-md-6) and Styles
        return `
            <!-- <div class="col-12 col-md-6 mb-3"> -->
            <div class="col-12 mb-3" style="max-width:500px;">
                <label class="form-label fw-bold">${index}. ${config.label} ${requiredTag}</label>
                <input 
                    id="${config.id}" 
                    name="${config.id}" 
                    type="${config.type || 'text'}"
                    class="${inputClasses.join(' ')}" 
                    style="${styleAttr}"
                    placeholder="${config.placeholder || ''}"
                    autocorrect="off"
                    spellcheck="false"
                    ${required}
                >
            </div>`;
        
    }

    //File upload
    createUploadTemplate(config, index) {
        return `
            <div class="col-12 mb-3">
                <label class="form-label fw-bold">${index}. ${config.label} ${config.required ? '<span style="color:red;">*</span>' : ''}</label>
                <div id="dropzone-${config.id}" class="upload-container border-dashed p-4 text-center rounded" 
                    style="border: 2px dashed #ccc; background: #fdfdfd; cursor: pointer;">
                    <input type="file" name="${config.id}" id="${config.id}" 
                        class="form-control d-none" 
                        accept="video/*" 
                        ${config.required ? 'required' : ''}>
                    <div class="upload-icon mb-2">🎬</div>
                    <p class="mb-0 text-muted">Drag & Drop your video here or <b>Click to Upload</b></p>
                    <small id="file-name-${config.id}" class="text-primary d-block mt-2 font-weight-bold"></small>
                </div>
                <div class="fs-4 mt-3"><i>*Video length must atleast 1 min</i></div>
            </div>`;
    }

    initLogic() {
        // Uppercase
        this.container.addEventListener('input', (e) => {
            if (e.target.classList.contains('force-upper')) {
                e.target.value = e.target.value.toUpperCase();
            }
        });

        // Button loading
        const formTag = this.container.closest('form');
        if (formTag) {
            formTag.addEventListener('submit', () => {
                const btn = document.getElementById('submit-btn');
                if (btn) {
                    btn.disabled = true;
                    btn.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Sending...`;
                }
            });
        }

        //File drag and drop
        // 2. Add Drag & Drop Logic
        const dropzones = this.container.querySelectorAll('.upload-container');
        dropzones.forEach(zone => {
            const input = zone.querySelector('input[type="file"]');
            const fileNameDisplay = zone.querySelector('small');

            // Click to trigger hidden input
            zone.addEventListener('click', () => input.click());

            // Drag effects
            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                zone.style.borderColor = AFWAN_GLOBAL_THEME.primaryColor;
                zone.style.background = "#eef6ff";
            });

            zone.addEventListener('dragleave', () => {
                zone.style.borderColor = "#ccc";
                zone.style.background = "#fdfdfd";
            });

            zone.addEventListener('drop', (e) => {
                e.preventDefault();
                input.files = e.dataTransfer.files;
                var file = input.files[0];
                var filename = file.name;
                var filesize = file.size / (1024*1024);
                var filesizedisplay = `${filesize.toFixed(1)} MB`;
                fileNameDisplay.innerText = "Selected: " + filename + " . " + filesizedisplay;
                zone.style.borderColor = "#28a745"; // Success green
            });

            // Update name when clicked manually
            input.addEventListener('change', () => {
                if (input.files.length > 0) {
                    var file = input.files[0];
                    var filename = file.name;
                    var filesize = file.size / (1024*1024);
                    var filesizedisplay = `${filesize.toFixed(1)} MB`;

                    fileNameDisplay.innerText = "Selected: " + filename + " . " + filesizedisplay;
                    zone.style.borderColor = "#28a745"; // Success green
                }
            });
        });
    }

    //HOW TO USE: =====================
    // <div>
    //     <div style="color:#535353" class="fs-2 mb-2">
    //         Seatleak Video Form
    //     </div>
    //     <form action="/seatleak/upload" method="post" enctype="multipart/form-data">
    //         <div id="dynamic-form-container"></div>
    //     </form>
    // </div>
    // <script>
    //     //Form
    //     const myFormFields = [
    //         { 
    //             id: 'file', 
    //             label: 'Seatleak Video', 
    //             type: 'file', 
    //             required: true 
    //         },
    //         { id: 'frmnumber', label: 'FRM Number', transform:['required', ''] }, //grey
    //         { id: 'name', label: 'Employee Name', transform: ['uppercase', '', 'required'] }, 
    //         { id: 'employeeid', label: 'Employee ID', transform: ['uppercase', '', 'required'] }, 
    //         { id: 'serialnumber', label: 'Serial Number', transform: ['uppercase', '', 'required'] },
    //         { id: 'allowable', label: 'Allowable', transform: ['uppercase', '', 'required'] },
    //         { id: 'remarks', label: 'Remarks', transform: ['', '', 'required'] },
    //     ];
    //     const form = new SmartFormEngine('dynamic-form-container');
    //     form.render(myFormFields, "Upload");
    // </script>
    // ==============================
}
//standardize filename
//back -> Home 🏠

class VideoGalleryEngine {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    render(videoData) {
        let html = '';
        videoData.forEach((d, index) => {
            var filename = d.filename;
            filename = filename.replace(".mp4", "");
            html += `
                <div class="selectorDIV mt-5 text-center fs-3 border rounded p-3">
                    <video class="video-player" width="900" height="600" controls>
                        <source src="static/videos/seatleak/${d.filename}" type="video/mp4">
                    </video>
                    <div class="d-flex justify-content-evenly">
                        <div>${d.name}</div>
                        <div class="duration-display">Loading...</div>
                        <div>${d.datetime}</div>
                    </div>
                    <div>${filename}</div>
                    <div>${d.serialnumber}</div>
                    <div class="text-left">FRM Number: ${d.frmnumber} </div>
                    <div class="text-left">Allowable: ${d.allowable} </div>
                    <div class="text-left">Remarks: ${d.remarks}</div>
                    <!--
                    <div class="fw-bold">${d.title}</div>
                    <div class="text-muted small">${d.serialnumber}</div>
                    <div class="text-start fs-5">FRM: ${d.frmnumber} | Allowable: ${d.allowable}</div>
                    <div class="text-start fs-6 italic text-secondary">Remarks: ${d.remarks}</div>
                    -->
                </div>`;
        });
        this.container.innerHTML = html;
        this.initVideoLogic();
    }

    initVideoLogic() {
        // We find all players we just created
        const players = this.container.querySelectorAll('.selectorDIV');
        
        players.forEach(player => {
            const video = player.querySelector('video');
            const display = player.querySelector('.duration-display');

            video.addEventListener("loadedmetadata", () => {
                const duration = video.duration;
                
                // Styling logic
                display.style.color = duration < 60 ? "red" : "darkgreen";
                
                // Formatting logic
                const min = Math.floor(duration / 60);
                const sec = Math.floor(duration % 60);
                display.textContent = `${min}:${sec < 10 ? '0' : ''}${sec} min`;
            });
        });
    }

    //HOW TO USE: ====================
    // <div id="video-gallery-container"></div>
    // <script>
    //     //Video container
    //     const videoData = {{ data | tojson }} || [];
    //     const gallery = new VideoGalleryEngine('video-gallery-container');
    //     gallery.render(videoData);
    // </script>
}

class BackButtonEngine {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    render(linkTo, type = "Back") {
        let html = "";

        if (type == "Back") {
            html += `
                <div class="selectorDIV" style="
                    font-size: 40px;
                    padding: 5px;
                    margin: 10px;
                    margin-left: 20px;
                    position: absolute;
                ">
                    <a href="${linkTo}" style="text-decoration: none;" >
                        🔙
                    </a>
                </div>`;
        }
        else if (type == "Home") {
            html += `
                <div class="" style="
                    font-size: 40px;
                    padding: 5px;
                    margin: 10px;
                    margin-left: 40px;
                    position: absolute;
                    background-color: transparent;
                ">
                    <a href="${linkTo}" style="text-decoration: none;" >
                        <div style="
                            display: flex;
                            justify-content: center;
                            align-items: center;
                        ">⬅️<span style="font-size: 20px;">Home</span></div>
                    </a>
                </div>`;
        }
        
        
        this.container.innerHTML = html;
        // this.initLogic();
    }

    // initLogic() {
       
    // }

    //HOW TO USE: ================================
    // <div id="dynamic-form-backbutton"></div>
    // <script>
    //     //Back Button
    //     const backbutton = new BackButtonEngine('dynamic-form-backbutton');
    //     backbutton.render("/seatleak", "Home");
    // </script>
}

class SeatleakSearchEngine {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    render(items) {
    // 1. Sort items by date (Newest First)
    const sortedItems = [...items].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    // 2. Group items by Date String (e.g., "Friday, 30 Jan")
    const groups = sortedItems.reduce((acc, item) => {
        const dateObj = new Date(item.created_at);
        const dateKey = dateObj.toLocaleDateString('en-GB', { 
            weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' 
        });
        
        if (!acc[dateKey]) acc[dateKey] = [];
        acc[dateKey].push(item);
        return acc;
    }, {});

    this.container.innerHTML = `
        <div class="row g-4 mt-3">
            <div class="col-md-8">
                <div class="selectorDIV p-4 shadow-sm position-relative">
                    <form action="/seatleak" method="get" class="mt-4">
                        <label class="fs-5 mb-2 text-secondary">🔍 Please input serial number</label>
                        <input name="serialnumber" type="text" class="form-control form-control-lg force-upper mb-3" placeholder="eg. F123456789" required>
                        <button type="submit" class="btn btn-primary btn-lg d-flex ms-auto">Search</button>
                    </form>
                </div>
                <div class="selectorDIV mt-4 p-4 text-center border-dashed" style="max-width: 180px;">
                    <div>New data?</div>
                    <a href="/seatleak/handle" class="btn btn-primary" style="color:white;">Submit new here</a>
                </div>
            </div>

            <div class="col-md-4">
                <div class="selectorDIV p-3 shadow-sm" style="max-height: 600px; overflow-y: auto; background: #f8f9fa;">
                    <div class="fw-bold mb-3 border-bottom pb-2">History Log</div>
                    
                    ${Object.keys(groups).map(date => `
                        <div class="date-group-header small fw-bold text-uppercase text-primary mt-3 mb-1" style="font-size: 1.5rem; letter-spacing: 1px;">
                            ${date}
                        </div>
                        <div class="card shadow-sm border-0 mb-3">
                            <table class="table table-hover mb-0">
                                <tbody>
                                    ${groups[date].map(d => {
                                        const timeOnly = new Date(d.created_at).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
                                        return `
                                            <tr>
                                                <td class="position-relative p-0" style="cursor: pointer;">
                                                    <a href="/seatleak?serialnumber=${d.serialnumber}" class="text-decoration-none d-block stretched-link p-2 text-dark">
                                                        <div class="d-flex justify-content-between align-items-center">
                                                            <span>🔹 <b>${d.serialnumber}</b></span>
                                                            <span class="text-muted" style="font-size: 1rem;">${timeOnly}</span>
                                                        </div>
                                                    </a>
                                                </td>
                                            </tr>
                                        `;
                                    }).join('')}
                                </tbody>
                            </table>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    this.initLogic();
}

    // <div style="position: absolute; right: 20px; top: 20px;">
    //     <a class="btn btn-dark me-2" href="/seatleak/log" title="Log" style="font-size: 25px;">📝</a>
    //     <a class="btn btn-dark" href="/seatleak/handle" title="Settings" style="font-size: 25px;">⚙️</a>
    // </div>

    initLogic() {
        // Use your existing uppercase logic
        const inputs = this.container.querySelectorAll('.force-upper');
        inputs.forEach(input => {
            input.addEventListener('input', (e) => {
                e.target.value = e.target.value.toUpperCase();
            });
        });
    }

    //HOW TO USE: =================
    // <div id="seatleak-main-system"></div>

    // <script>
    //     // Data from Flask
    //     const historyItems = {{ items | tojson }};

    //     // Initialize the new Search Engine
    //     const searchSystem = new SeatleakSearchEngine('seatleak-main-system');
    //     searchSystem.render(historyItems);
    // </script>
}