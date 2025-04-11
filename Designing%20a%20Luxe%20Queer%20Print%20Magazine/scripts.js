// Luxe Queer Magazine Scripts

document.addEventListener('DOMContentLoaded', function() {
    // Header scroll effect
    const header = document.querySelector('header');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            header.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
            header.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        } else {
            header.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
            header.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        }
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Handle feature links (placeholder pages)
    document.querySelectorAll('.feature-link, a[href*="features/"], a[href="octavia.html"], a[href="subscribe.html"]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const pageName = this.getAttribute('href').split('/').pop().replace('.html', '');
            let message = '';
            
            switch(pageName) {
                case 'fashion':
                    message = 'The Fashion section will showcase boundary-dissolving couture that celebrates the full spectrum of identity and expression.';
                    break;
                case 'art':
                    message = 'The Art & Culture section will spotlight visionaries who transform cultural landscapes through a queer perspective.';
                    break;
                case 'travel':
                    message = 'The Travel section will feature destinations that don\'t just welcome queer travelers—they celebrate them in opulent style.';
                    break;
                case 'technology':
                    message = 'The Technology section will highlight innovations that are reshaping our world with inclusivity and luxury at their core.';
                    break;
                case 'luxury':
                    message = 'The Luxury section will redefine opulence through authenticity, sustainability, and queer excellence.';
                    break;
                case 'blue-lipstick-edit':
                    message = 'The Blue Lipstick Edit is our signature series featuring Octavia\'s bold takes on luxury and queer culture.';
                    break;
                case 'octavia':
                    message = 'The Octavia Opulence³ page will provide a deeper look into our editorial persona and AI-powered digital human ambassador.';
                    break;
                case 'subscribe':
                    message = 'Thank you for your interest in subscribing to Luxe Queer magazine! Subscription options will be available when we launch.';
                    break;
                default:
                    message = 'This content is coming soon to Luxe Queer magazine!';
            }
            
            showModal(message);
        });
    });
    
    // Animation for blue lipstick elements
    const blueElements = document.querySelectorAll('.blue-lipstick-mark, .blue-lipstick-accent');
    
    blueElements.forEach(element => {
        element.addEventListener('mouseover', function() {
            this.style.transform = this.classList.contains('blue-lipstick-mark') 
                ? 'rotate(30deg) scale(1.1)' 
                : 'scaleX(1.2)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        element.addEventListener('mouseout', function() {
            this.style.transform = this.classList.contains('blue-lipstick-mark') 
                ? 'rotate(15deg)' 
                : 'scaleX(1)';
        });
    });
    
    // Newsletter form submission
    const newsletterForm = document.querySelector('.newsletter-form');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const emailInput = this.querySelector('input[type="email"]');
            const email = emailInput.value.trim();
            
            if (email && isValidEmail(email)) {
                // In a real implementation, this would send the data to a server
                showModal('Thank you for subscribing to the Luxe Queer newsletter!');
                emailInput.value = '';
            } else {
                showModal('Please enter a valid email address.');
            }
        });
    }
    
    // Helper function to validate email
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    // Octavia quote rotation
    const quotes = [
        '"Darling, luxury isn\'t what you have—it\'s how completely you own who you are."',
        '"In a world of beige conformity, wear blue lipstick and make them remember you."',
        '"True opulence is the freedom to be authentically, unapologetically yourself."',
        '"Luxury without purpose is just expensive emptiness."',
        '"The most exquisite accessory you can wear is your truth."'
    ];
    
    const bannerQuote = document.querySelector('.blue-lipstick-banner h2');
    
    if (bannerQuote) {
        let currentQuote = 0;
        
        setInterval(() => {
            currentQuote = (currentQuote + 1) % quotes.length;
            
            // Fade out
            bannerQuote.style.opacity = '0';
            
            setTimeout(() => {
                // Change text and fade in
                bannerQuote.textContent = quotes[currentQuote];
                bannerQuote.style.opacity = '1';
            }, 500);
        }, 8000);
    }
    
    // Create modal for messages
    function createModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close-button">&times;</span>
                <div class="modal-body"></div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Add styles for modal
        const style = document.createElement('style');
        style.textContent = `
            .modal {
                display: none;
                position: fixed;
                z-index: 2000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.7);
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            .modal.show {
                opacity: 1;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .modal-content {
                background-color: white;
                padding: 2rem;
                border-radius: 5px;
                max-width: 500px;
                width: 90%;
                position: relative;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                transform: translateY(-20px);
                transition: transform 0.3s ease;
            }
            .modal.show .modal-content {
                transform: translateY(0);
            }
            .close-button {
                position: absolute;
                top: 10px;
                right: 15px;
                font-size: 1.5rem;
                cursor: pointer;
            }
            .close-button:hover {
                color: var(--accent-color);
            }
            .modal-body {
                margin-top: 1rem;
                font-family: var(--font-body);
                line-height: 1.6;
            }
        `;
        document.head.appendChild(style);
        
        // Close button functionality
        const closeButton = modal.querySelector('.close-button');
        closeButton.addEventListener('click', () => {
            modal.classList.remove('show');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        });
        
        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeButton.click();
            }
        });
        
        return modal;
    }
    
    // Show modal with message
    function showModal(message) {
        let modal = document.querySelector('.modal');
        
        if (!modal) {
            modal = createModal();
        }
        
        const modalBody = modal.querySelector('.modal-body');
        modalBody.textContent = message;
        
        modal.style.display = 'flex';
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
    }
    
    // Handle social media links
    document.querySelectorAll('a[href^="https://instagram.com"], a[href^="https://twitter.com"], a[href^="https://linkedin.com"]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const platform = this.getAttribute('href').includes('instagram') ? 'Instagram' : 
                            this.getAttribute('href').includes('twitter') ? 'Twitter' : 'LinkedIn';
            showModal(`Luxe Queer will be coming soon to ${platform}! Follow us for updates on luxury through a queer lens.`);
        });
    });
    
    // Handle email link
    document.querySelector('a[href^="mailto:"]').addEventListener('click', function(e) {
        e.preventDefault();
        showModal('Contact us at contact@luxequeer.com for inquiries about Luxe Queer magazine.');
    });
});
