
        // Header Scroll Effect
        window.addEventListener('scroll', function() {
            const header = document.getElementById('header');
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });

        // Mobile Menu Toggle
        const hamburger = document.querySelector('.hamburger');
        const navLinks = document.querySelector('.nav-links');

        hamburger.addEventListener('click', function() {
            this.classList.toggle('active');
            navLinks.classList.toggle('active');
        });

        // Close mobile menu when clicking a link
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
            });
        });

        // Form Submission
        const form = document.getElementById('form');
        const loading = document.querySelector('.loading');

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show loading spinner
            loading.classList.add('active');
            
            // Simulate form submission
            setTimeout(() => {
                loading.classList.remove('active');
                alert('Message sent successfully!');
                form.reset();
            }, 2000);
        });

        // Animate elements on scroll
        function animateOnScroll() {
            const elements = document.querySelectorAll('.about-img, .about-text, .skill-category, .project-card, .contact-info, .contact-form');
            
            elements.forEach(element => {
                const elementPosition = element.getBoundingClientRect().top;
                const screenPosition = window.innerHeight / 1.3;
                
                if (elementPosition < screenPosition) {
                    element.classList.add('animated');
                }
            });
        }

        // Animate skill bars
        function animateSkillBars() {
            const skillBars = document.querySelectorAll('.skill-progress');
            
            skillBars.forEach(bar => {
                const width = bar.getAttribute('data-width');
                bar.style.width = width + '%';
            });
        }

        // Initialize animations when page loads
        window.addEventListener('load', function() {
            animateSkillBars();
            animateOnScroll();
        });

        // Continue animations on scroll
        window.addEventListener('scroll', animateOnScroll);

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 80,
                        behavior: 'smooth'
                    });
                }
            });
        });

        // Form field animations
        document.querySelectorAll('.form-group input, .form-group textarea').forEach(field => {
            field.addEventListener('focus', function() {
                this.parentNode.querySelector('label').style.color = 'var(--primary-color)';
            });
            
            field.addEventListener('blur', function() {
                if (!this.value) {
                    this.parentNode.querySelector('label').style.color = 'var(--text-light)';
                }
            });
        });