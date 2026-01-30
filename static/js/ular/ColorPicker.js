/**
 * ColorPicker - A reusable color picker component
 * Usage:
 *   const picker = new ColorPicker('mySelectId', 'myPreviewId');
 *   picker.getValue() - get selected color
 */
class ColorPicker {
    constructor(selectId, previewId = null) {
        this.selectElement = document.getElementById(selectId);
        this.previewElement = previewId ? document.getElementById(previewId) : null;
        
        if (!this.selectElement) {
            console.error(`ColorPicker: Select element with id '${selectId}' not found`);
            return;
        }
        
        this.colors = [
            { value: 'aliceblue', name: 'Alice Blue' },
            { value: 'antiquewhite', name: 'Antique White' },
            { value: 'aqua', name: 'Aqua' },
            { value: 'aquamarine', name: 'Aquamarine' },
            { value: 'azure', name: 'Azure' },
            { value: 'beige', name: 'Beige' },
            { value: 'bisque', name: 'Bisque' },
            { value: 'black', name: 'Black' },
            { value: 'blanchedalmond', name: 'Blanched Almond' },
            { value: 'blue', name: 'Blue' },
            { value: 'blueviolet', name: 'Blue Violet' },
            { value: 'brown', name: 'Brown' },
            { value: 'burlywood', name: 'Burlywood' },
            { value: 'cadetblue', name: 'Cadet Blue' },
            { value: 'chartreuse', name: 'Chartreuse' },
            { value: 'chocolate', name: 'Chocolate' },
            { value: 'coral', name: 'Coral' },
            { value: 'cornflowerblue', name: 'Cornflower Blue' },
            { value: 'cornsilk', name: 'Cornsilk' },
            { value: 'crimson', name: 'Crimson' },
            { value: 'cyan', name: 'Cyan' },
            { value: 'darkblue', name: 'Dark Blue' },
            { value: 'darkcyan', name: 'Dark Cyan' },
            { value: 'darkgoldenrod', name: 'Dark Goldenrod' },
            { value: 'darkgray', name: 'Dark Gray' },
            { value: 'darkgreen', name: 'Dark Green' },
            { value: 'darkkhaki', name: 'Dark Khaki' },
            { value: 'darkmagenta', name: 'Dark Magenta' },
            { value: 'darkolivegreen', name: 'Dark Olive Green' },
            { value: 'darkorange', name: 'Dark Orange' },
            { value: 'darkorchid', name: 'Dark Orchid' },
            { value: 'darkred', name: 'Dark Red' },
            { value: 'darksalmon', name: 'Dark Salmon' },
            { value: 'darkseagreen', name: 'Dark Sea Green' },
            { value: 'darkslateblue', name: 'Dark Slate Blue' },
            { value: 'darkslategray', name: 'Dark Slate Gray' },
            { value: 'darkturquoise', name: 'Dark Turquoise' },
            { value: 'darkviolet', name: 'Dark Violet' },
            { value: 'deeppink', name: 'Deep Pink' },
            { value: 'deepskyblue', name: 'Deep Sky Blue' },
            { value: 'dimgray', name: 'Dim Gray' },
            { value: 'dodgerblue', name: 'Dodger Blue' },
            { value: 'firebrick', name: 'Firebrick' },
            { value: 'floralwhite', name: 'Floral White' },
            { value: 'forestgreen', name: 'Forest Green' },
            { value: 'fuchsia', name: 'Fuchsia' },
            { value: 'gainsboro', name: 'Gainsboro' },
            { value: 'ghostwhite', name: 'Ghost White' },
            { value: 'gold', name: 'Gold' },
            { value: 'goldenrod', name: 'Goldenrod' },
            { value: 'gray', name: 'Gray' },
            { value: 'green', name: 'Green' },
            { value: 'greenyellow', name: 'Green Yellow' },
            { value: 'honeydew', name: 'Honeydew' },
            { value: 'hotpink', name: 'Hot Pink' },
            { value: 'indianred', name: 'Indian Red' },
            { value: 'indigo', name: 'Indigo' },
            { value: 'ivory', name: 'Ivory' },
            { value: 'khaki', name: 'Khaki' },
            { value: 'lavender', name: 'Lavender' },
            { value: 'lavenderblush', name: 'Lavender Blush' },
            { value: 'lawngreen', name: 'Lawn Green' },
            { value: 'lemonchiffon', name: 'Lemon Chiffon' },
            { value: 'lightblue', name: 'Light Blue' },
            { value: 'lightcoral', name: 'Light Coral' },
            { value: 'lightcyan', name: 'Light Cyan' },
            { value: 'lightgoldenrodyellow', name: 'Light Goldenrod Yellow' },
            { value: 'lightgray', name: 'Light Gray' },
            { value: 'lightgreen', name: 'Light Green' },
            { value: 'lightpink', name: 'Light Pink' },
            { value: 'lightsalmon', name: 'Light Salmon' },
            { value: 'lightseagreen', name: 'Light Sea Green' },
            { value: 'lightskyblue', name: 'Light Sky Blue' },
            { value: 'lightslategray', name: 'Light Slate Gray' },
            { value: 'lightsteelblue', name: 'Light Steel Blue' },
            { value: 'lightyellow', name: 'Light Yellow' },
            { value: 'lime', name: 'Lime' },
            { value: 'limegreen', name: 'Lime Green' },
            { value: 'linen', name: 'Linen' },
            { value: 'magenta', name: 'Magenta' },
            { value: 'maroon', name: 'Maroon' },
            { value: 'mediumaquamarine', name: 'Medium Aquamarine' },
            { value: 'mediumblue', name: 'Medium Blue' },
            { value: 'mediumorchid', name: 'Medium Orchid' },
            { value: 'mediumpurple', name: 'Medium Purple' },
            { value: 'mediumseagreen', name: 'Medium Sea Green' },
            { value: 'mediumslateblue', name: 'Medium Slate Blue' },
            { value: 'mediumspringgreen', name: 'Medium Spring Green' },
            { value: 'mediumturquoise', name: 'Medium Turquoise' },
            { value: 'mediumvioletred', name: 'Medium Violet Red' },
            { value: 'midnightblue', name: 'Midnight Blue' },
            { value: 'mintcream', name: 'Mint Cream' },
            { value: 'mistyrose', name: 'Misty Rose' },
            { value: 'moccasin', name: 'Moccasin' },
            { value: 'navajowhite', name: 'Navajo White' },
            { value: 'navy', name: 'Navy' },
            { value: 'oldlace', name: 'Old Lace' },
            { value: 'olive', name: 'Olive' },
            { value: 'olivedrab', name: 'Olive Drab' },
            { value: 'orange', name: 'Orange' },
            { value: 'orangered', name: 'Orange Red' },
            { value: 'orchid', name: 'Orchid' },
            { value: 'palegoldenrod', name: 'Pale Goldenrod' },
            { value: 'palegreen', name: 'Pale Green' },
            { value: 'paleturquoise', name: 'Pale Turquoise' },
            { value: 'palevioletred', name: 'Pale Violet Red' },
            { value: 'papayawhip', name: 'Papaya Whip' },
            { value: 'peachpuff', name: 'Peach Puff' },
            { value: 'peru', name: 'Peru' },
            { value: 'pink', name: 'Pink' },
            { value: 'plum', name: 'Plum' },
            { value: 'powderblue', name: 'Powder Blue' },
            { value: 'purple', name: 'Purple' },
            { value: 'rebeccapurple', name: 'Rebecca Purple' },
            { value: 'red', name: 'Red' },
            { value: 'rosybrown', name: 'Rosy Brown' },
            { value: 'royalblue', name: 'Royal Blue' },
            { value: 'saddlebrown', name: 'Saddle Brown' },
            { value: 'salmon', name: 'Salmon' },
            { value: 'sandybrown', name: 'Sandy Brown' },
            { value: 'seagreen', name: 'Sea Green' },
            { value: 'seashell', name: 'Seashell' },
            { value: 'sienna', name: 'Sienna' },
            { value: 'silver', name: 'Silver' },
            { value: 'skyblue', name: 'Sky Blue' },
            { value: 'slateblue', name: 'Slate Blue' },
            { value: 'slategray', name: 'Slate Gray' },
            { value: 'snow', name: 'Snow' },
            { value: 'springgreen', name: 'Spring Green' },
            { value: 'steelblue', name: 'Steel Blue' },
            { value: 'tan', name: 'Tan' },
            { value: 'teal', name: 'Teal' },
            { value: 'thistle', name: 'Thistle' },
            { value: 'tomato', name: 'Tomato' },
            { value: 'turquoise', name: 'Turquoise' },
            { value: 'violet', name: 'Violet' },
            { value: 'wheat', name: 'Wheat' },
            { value: 'white', name: 'White' },
            { value: 'whitesmoke', name: 'White Smoke' },
            { value: 'yellow', name: 'Yellow' },
            { value: 'yellowgreen', name: 'Yellow Green' }
        ];
        
        this.init();
    }
    
    init() {
        // Clear existing options
        this.selectElement.innerHTML = '';
        
        // Add placeholder option
        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = 'Select Color';
        placeholderOption.disabled = true;
        placeholderOption.selected = true;
        this.selectElement.appendChild(placeholderOption);
        
        // Add all color options
        this.colors.forEach(color => {
            const option = document.createElement('option');
            option.value = color.value;
            option.textContent = color.name;
            this.selectElement.appendChild(option);
        });
        
        // Add event listener for color preview
        if (this.previewElement) {
            this.selectElement.addEventListener('change', () => {
                this.updatePreview();
            });
            // Set initial preview
            this.updatePreview();
        }
    }
    
    updatePreview() {
        if (this.previewElement) {
            const selectedColor = this.selectElement.value || 'black';
            this.previewElement.style.backgroundColor = selectedColor;
        }
    }
    
    getValue() {
        return this.selectElement.value || 'black';
    }
    
    setValue(color) {
        this.selectElement.value = color;
        this.updatePreview();
    }
    
    // Static method to create color picker HTML structure
    static createHTML(selectId, previewId, containerClass = '') {
        return `
            <div class="${containerClass}" style="display: flex; gap: 10px; align-items: center;">
                <select id="${selectId}" class="form-control" style="flex: 1;"></select>
                <div id="${previewId}" style="width: 30px; height: 30px; border-radius: 50%; border: 2px solid #ccc; background-color: black;"></div>
            </div>
        `;
    }
}
