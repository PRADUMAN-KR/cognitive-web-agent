document.addEventListener("DOMContentLoaded", () => {
    // Parallax effect for hero shapes
    document.addEventListener("mousemove", (e) => {
      const shapes = document.querySelectorAll(".hero-shapes .shape")
      const x = e.clientX / window.innerWidth
      const y = e.clientY / window.innerHeight
  
      shapes.forEach((shape, index) => {
        const speed = (index + 1) * 20
        const xOffset = (x - 0.5) * speed
        const yOffset = (y - 0.5) * speed
  
        shape.style.transform = `translate(${xOffset}px, ${yOffset}px)`
      })
    })
  
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", function (e) {
        e.preventDefault()
  
        const targetId = this.getAttribute("href")
        if (targetId === "#") return
  
        const targetElement = document.querySelector(targetId)
        if (targetElement) {
          window.scrollTo({
            top: targetElement.offsetTop - 80,
            behavior: "smooth",
          })
        }
      })
    })
  
    // Header scroll effect
    const header = document.querySelector(".main-header")
    window.addEventListener("scroll", () => {
      if (window.scrollY > 50) {
        header.style.padding = "15px 0"
        header.style.background = "rgba(10, 10, 26, 0.95)"
      } else {
        header.style.padding = "20px 0"
        header.style.background = "rgba(10, 10, 26, 0.8)"
      }
    })
  })
  

// targeting the create bot button

document.getElementById('createBotBtn').addEventListener('click', function() {
  const modal = new bootstrap.Modal(document.getElementById('webBotModal'));
  modal.show();
});

