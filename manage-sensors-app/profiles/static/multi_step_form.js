var step = 1
const step1 = document.getElementById('formPart1');
const step2 = document.getElementById('formPart2');
const step3 = document.getElementById('formPart3');

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('input[type="checkbox"][name$="-DELETE"]').forEach(delCheckbox => {
    delCheckbox.addEventListener('change', deleteListener);
  });
});

function deleteListener() {
  const formRow = this.closest('.form-row');
  if (this.checked) {
    formRow.querySelectorAll('input[required], select[required], textarea[required]').forEach(el => {
      el.removeAttribute('required');
    });
    formRow.classList.add('d-none');
  }
}

function nextStep() {
  if (validateState(step)) {
    step +=1;
    step = Math.min(3, step);
    updateFormStep();
  }
}

function validateState(step) {
  let stepContainer;
  switch (step) {
    case 1:
      stepContainer = step1;
      break;
    case 2:
      stepContainer = step2;
      break;
    case 3:
      stepContainer = step3;
      break;
  }
        
  const inputs = stepContainer.querySelectorAll('input[required], select[required]');

  for (const input of inputs) {
    if (!input.checkValidity()) {
      console.log(input);
      input.reportValidity();
      return false;
    }
  }
  return true;
}

function markForDelete(btn) {
    const container = btn.closest('div');
    const checkbox = container.querySelector('input[type="checkbox"]');
    if (checkbox) {
      checkbox.checked = true;
      container.classList.add("d-none");
    }
  }

function prevStep() {
  step -=1;
  step = Math.max(1, step);
  updateFormStep();
}

function updateFormStep() {
  step1.classList.add("d-none");
  step2.classList.add("d-none");
  step3.classList.add("d-none");
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  prevBtn.classList.add("d-none");
  nextBtn.classList.add("d-none");
  switch (step) {
      case 1:
        nextBtn.classList.remove("d-none");
        step1.classList.remove("d-none");
        break;
      case 2:
        prevBtn.classList.remove("d-none");
        nextBtn.classList.remove("d-none");
        step2.classList.remove("d-none");
        break;
      case 3:
        prevBtn.classList.remove("d-none");
        step3.classList.remove("d-none");
        updateResources();
        break;
  }
}

window.addEventListener("load", function () {

  //document.getElementById('id_label-TOTAL_FORMS').value = 0;
  //document.getElementById('id_resource-TOTAL_FORMS').value = 1;
  //document.getElementById('id_command-TOTAL_FORMS').value = 0;
  //document.getElementById('id_operation-TOTAL_FORMS').value = 0;
  //document.getElementById('id_properties-TOTAL_FORMS').value = 1;
});



function addLabelForm() {
  const formsetContainer = document.getElementById('label-container');
  const emptyFormDiv = document.getElementById('empty-label-form');
  let newFormHtml = emptyFormDiv.innerHTML;
  const totalFormsInput = document.getElementById('id_label-TOTAL_FORMS');
  let totalForms = parseInt(totalFormsInput.value);


  // Actualizar los índices en el HTML
  const regex = new RegExp('__prefix__', 'g');
  newFormHtml = newFormHtml.replace(regex, totalForms);
  
  // Añadir nuevo formulario al container
  const newDiv = document.createElement('div');
  newDiv.classList.add('form-row');
  newDiv.innerHTML = newFormHtml;
  formsetContainer.appendChild(newDiv);
  
  newDiv.querySelectorAll('input[type="checkbox"][name$="-DELETE"]').forEach(delCheckbox => {
    delCheckbox.addEventListener('change', deleteListener);
  });

  // Actualizar el total de formularios
  totalFormsInput.value = totalForms + 1;
}
function addFormHelper(prefix, container){
  const totalForms = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
  const currentCount = parseInt(totalForms.value);
  
  const emptyFormDiv = document.getElementById(`empty-${prefix}-form`);
  let newFormHtml = emptyFormDiv.innerHTML;
  
  const regex = new RegExp('__prefix__', 'g');
  newFormHtml = newFormHtml.replace(regex, currentCount);
  const newDiv = document.createElement('div');
  newDiv.classList.add('form-row', 'mb-3', 'border', 'rounded', 'p-3', 'bg-white', 'position-relative');
  newDiv.innerHTML = newFormHtml;
  container.appendChild(newDiv);
  totalForms.value = currentCount + 1;

  newDiv.querySelectorAll('input[type="checkbox"][name$="-DELETE"]').forEach(delCheckbox => {
    delCheckbox.addEventListener('change', deleteListener);
  });
  return currentCount;
}

function addCommandForm() {
  const container = document.getElementById('command-container');
  const commandFormId = addFormHelper('command', container);
  container.querySelector(`#id_command-${commandFormId}-name`).setAttribute('required', 'required');
  container.querySelector(`#id_command-${commandFormId}-readWrite`).setAttribute('required', 'required');
  operationsContainerDiv = document.createElement('div');
  operationsContainerDiv.id = `${commandFormId}-operation-container`;
  container.lastElementChild.appendChild(operationsContainerDiv);
  addOperationForm(commandFormId);
}

function addOperationForm(commandFormId){
  const container = document.getElementById(`${commandFormId}-operation-container`);
  const currentCount = addFormHelper('operation', container);
  container.querySelector(`#id_operation-${currentCount}-resource`).setAttribute('required', 'required');
  container.querySelector(`#id_operation-${currentCount}-defaultValue`).setAttribute('required', 'required');
  //Remove command select and set to command
  const command = container.querySelector(`#id_operation-${currentCount}-command`);
  command.value = parseInt(commandFormId);
  command.parentElement.classList.add('d-none');
  updateResources();
}


function addResourceForm() {
  const container = document.getElementById('resource-container');
  const totalForms = document.getElementById('id_resource-TOTAL_FORMS');
  const currentCount = parseInt(totalForms.value);
  const newForm = container.children[0].cloneNode(true);

  newForm.classList.remove('d-none');
  
  // Actualiza atributos de los campos (name, id, for)
  const updateAttributes = (element) => {
    ['for', 'id', 'name'].forEach(attr => {
      if (element.hasAttribute(attr)) {
        element.setAttribute(attr, element.getAttribute(attr).replace(/-\d+-/, `-${currentCount}-`));
      }
    });
  };

  // Actualiza cada input, select y textarea
  newForm.querySelectorAll('input, select, textarea, label').forEach(el => {
    updateAttributes(el);
    if (el.tagName !== 'LABEL') {
      if (el.type === 'checkbox' || el.type === 'radio') {
        el.checked = false;
      } else {
        el.value = '';
      }
    }
  });
  
  
  const totalPropertiesForms = document.getElementById('id_properties-TOTAL_FORMS');
  newForm.querySelectorAll('[name^="properties-"], [id^="id_properties-"]').forEach(el => {
    updateAttributes(el);
  });
  
  container.appendChild(newForm);
  newForm.querySelectorAll('input[type="checkbox"][name$="-DELETE"]').forEach(delCheckbox => {
    delCheckbox.addEventListener('change', deleteListener);
  });

  totalPropertiesForms.value = currentCount + 1;
  totalForms.value = currentCount + 1;

  container.querySelector(`#id_resource-${currentCount}-name`).setAttribute('required', 'required');
  container.querySelector(`#id_resource-${currentCount}-description`).setAttribute('required', 'required');
  container.querySelector(`#id_properties-${currentCount}-valueType`).setAttribute('required', 'required');
  container.querySelector(`#id_properties-${currentCount}-readWrite`).setAttribute('required', 'required');

}


function updateResources() {
  const res_container = document.getElementById('resource-container');
  const resources_array = Array.from(res_container.children);
  const options = resources_array.reduce( (acc, child, index) => {
    const checkbox = child.querySelector('input[type="checkbox"][id^="id_resource-"][id$="-DELETE"]');
    if (checkbox && ! checkbox.checked) {
      acc.push({
        value: index,
        text: child.firstElementChild.lastElementChild.value,
      })
    }
    return acc
  }, [])
  const com_container = document.getElementById('command-container');
  const selects = Array.from(
    com_container.querySelectorAll('select[id^="id_operation-"][id$="-resource"]')
  )
  selects.forEach(select => {
    // Limpiar opciones actuales
    const value = select.value;
    select.innerHTML = '';

    // Agregar nuevas opciones
    options.forEach(opt => {
      const option = document.createElement('option');
      option.value = opt.value;
      option.textContent = opt.text;
      select.appendChild(option);
    });
    select.value = value;

  });
  

}