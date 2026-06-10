document.addEventListener('DOMContentLoaded', function() {
    const photoInput = document.getElementById('photoInput');
    const previewWrapper = document.getElementById('preview-wrapper');
    const previewImage = document.getElementById('single-image-preview');

    if (photoInput) {
        photoInput.addEventListener('change', function() {
            const file = this.files[0]; 
            
            if (file && file.type.startsWith('image/')) {
                const imageUrl = URL.createObjectURL(file);

                previewImage.src = imageUrl;
                previewWrapper.classList.remove('d-none');
                
                setTimeout(() => previewWrapper.classList.add('show'), 50);

                previewImage.onload = () => {
                    URL.revokeObjectURL(imageUrl);
                };
            } else {
                previewImage.src = '';
                previewWrapper.classList.remove('show');
                setTimeout(() => previewWrapper.classList.add('d-none'), 150);
            }
        });
    }
});
