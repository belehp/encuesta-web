// Funcionalidad para el formulario de encuesta
document.addEventListener("DOMContentLoaded", () => {
  const anonymousSwitch = document.getElementById("anonymousSwitch")
  const personalData = document.getElementById("personalData")
  const surveyForm = document.getElementById("surveyForm")

  // Manejar el switch de encuesta anónima
  if (anonymousSwitch && personalData) {
    anonymousSwitch.addEventListener("change", function () {
      if (this.checked) {
        personalData.style.display = "none"
        // Remover required de campos personales
        personalData.querySelectorAll("input, select").forEach((field) => {
          field.removeAttribute("required")
        })
      } else {
        personalData.style.display = "block"
        // Agregar required a campos personales
        personalData.querySelectorAll("input, select").forEach((field) => {
          if (field.id !== "anonymousSwitch") {
            field.setAttribute("required", "required")
          }
        })
      }
    })
  }

  // Manejar envío del formulario
  if (surveyForm) {
    surveyForm.addEventListener("submit", function (e) {
      e.preventDefault()

      const formData = new FormData(this)
      const isAnonymous = anonymousSwitch.checked

      // Preparar datos para enviar
      const surveyData = {
        is_anonymous: isAnonymous,
        responses: {},
      }

      // Agregar datos personales si no es anónima
      if (!isAnonymous) {
        surveyData.nombre = document.getElementById("nombre").value
        surveyData.email = document.getElementById("email").value
        surveyData.edad = Number.parseInt(document.getElementById("edad").value)
        surveyData.sexo = document.getElementById("sexo").value
      }

      // Recopilar respuestas
      const radioButtons = this.querySelectorAll('input[type="radio"]:checked')
      radioButtons.forEach((radio) => {
        const questionId = radio.name.replace("question_", "")
        surveyData.responses[questionId] = radio.value
      })

      // Validar que todas las preguntas estén respondidas
      const totalQuestions = this.querySelectorAll('input[type="radio"]').length / 4 // 4 opciones por pregunta
      if (Object.keys(surveyData.responses).length !== totalQuestions) {
        alert("Por favor, responde todas las preguntas.")
        return
      }

      // Enviar datos
      const submitButton = this.querySelector('button[type="submit"]')
      const originalText = submitButton.innerHTML
      submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enviando...'
      submitButton.disabled = true

      fetch("/api/submit-survey", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(surveyData),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // Mostrar resultado SIN puntaje ni clasificación
            const modalBody = document.querySelector("#successModal .modal-body")
            modalBody.innerHTML = `
        <div class="text-center">
          <h5>✅ Evaluación Completada</h5>
          <p>Gracias por completar la evaluación de violencia intrafamiliar.</p>
          <div class="alert alert-info">
            <strong>📋 Tu respuesta ha sido registrada correctamente.</strong><br>
            <small>La información será utilizada para mejorar los servicios de salud.</small>
          </div>
          <div class="alert alert-warning">
            <strong>💡 Recuerda:</strong> Si necesitas ayuda, siempre puedes acudir a un profesional de la salud, asistente social o Carabineros.
          </div>
        </div>
      `
            const successModal = new bootstrap.Modal(document.getElementById("successModal"))
            successModal.show()
          } else {
            alert("Error al enviar la evaluación: " + (data.error || "Error desconocido"))
          }
        })
        .catch((error) => {
          console.error("Error:", error)
          alert("Error al enviar la encuesta. Por favor, intenta nuevamente.")
        })
        .finally(() => {
          submitButton.innerHTML = originalText
          submitButton.disabled = false
        })
    })
  }

  // Animaciones suaves para las cards
  const cards = document.querySelectorAll(".hover-card")
  cards.forEach((card) => {
    card.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-5px)"
    })

    card.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0)"
    })
  })
})

// Función para validar email
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

// Función para mostrar mensajes de error
function showError(message) {
  const alertDiv = document.createElement("div")
  alertDiv.className = "alert alert-danger alert-dismissible fade show"
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `

  const container = document.querySelector(".container")
  container.insertBefore(alertDiv, container.firstChild)

  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    if (alertDiv.parentNode) {
      alertDiv.remove()
    }
  }, 5000)
}
