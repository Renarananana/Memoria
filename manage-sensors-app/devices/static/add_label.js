

window.onload = function() {
  document.getElementById('id_label-TOTAL_FORMS').value = 0;
}

function addLabelForm() {
  const formsetContainer = document.getElementById('label-container');
  const emptyFormDiv = document.getElementById('empty-label-form');
  let newFormHtml = emptyFormDiv.innerHTML;
  const totalFormsInput = document.querySelector('#id_label-TOTAL_FORMS');
  let totalForms = parseInt(totalFormsInput.value);


  // Actualizar los índices en el HTML
  const regex = new RegExp('__prefix__', 'g');
  newFormHtml = newFormHtml.replace(regex, totalForms);
  
  // Añadir nuevo formulario al container
  const newDiv = document.createElement('div');
  newDiv.classList.add('form-row');
  newDiv.innerHTML = newFormHtml;
  formsetContainer.appendChild(newDiv);
  
  // Actualizar el total de formularios
  totalFormsInput.value = totalForms + 1;
}