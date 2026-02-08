document.addEventListener("DOMContentLoaded", () => {
  const newTransactionButton = document.getElementById("new-transaction-btn");
  const addNewAccountButton = document.getElementById("add-new-account-btn");
  const settingsButton = document.getElementById("settings-btn");
  const transactionForm = document.getElementById("transaction-form");
  const settingsForm = document.getElementById("settings-form");
  const addaccountForm = document.getElementById("addAccount-form");


  if (newTransactionButton) {
      newTransactionButton.addEventListener("click", () => {
          toggleVisibility(transactionForm);
      });
  }

  if (addNewAccountButton) {
      addNewAccountButton.addEventListener("click", () => {
          toggleVisibility(addaccountForm);
      });
  }

  if (settingsButton) {
      settingsButton.addEventListener("click", () => {
          toggleVisibility(settingsForm);
      });
  }
    document.querySelectorAll('.edit').forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            const transactionId = button.getAttribute('data-transactionid');
            const form = document.getElementById(`edit-form-${transactionId}`);
            if (form) {
                form.classList.toggle('hidden');
                if (!form.classList.contains('hidden')) {
                    form.scrollIntoView({ behavior: 'smooth' });
                }
            } else {
                console.error(`Formulář s ID edit-form-${transactionId} nebyl nalezen.`);
            }
        });
    });

    document.querySelectorAll('.edit-budget').forEach(button => {
        button.addEventListener('click', (event) => {
            const userId = event.target.getAttribute('data-userid');
            const form = document.getElementById(`editbudget-form-${userId}`);
            if (form) {
                form.classList.toggle('hidden');
                if (!form.classList.contains('hidden')) {
                    form.scrollIntoView({ behavior: 'smooth' });
                }
            } else {
                console.error(`Formulář s ID edit-budget-${userId} nebyl nalezen.`);
            }
        });
    });

    document.querySelectorAll('.edit-access').forEach(button => {
        button.addEventListener('click', (event) => {
            const userId = event.target.getAttribute('data-userid');
            const form = document.getElementById(`rights-form-${userId}`);
            if (form) {
                form.classList.toggle('hidden');
                if (!form.classList.contains('hidden')) {
                    form.scrollIntoView({ behavior: 'smooth' });
                }
            } else {
                console.error(`Formulář s ID edit-access-${userId} nebyl nalezen.`);
            }
        });
    });

    document.querySelectorAll('.delete-access').forEach(button => {
        button.addEventListener('click', (event) => {
            const userId = event.target.getAttribute('data-userid');
            const form = document.getElementById(`delete-rights-form-${userId}`);
            if (form) {
                form.classList.toggle('hidden');
                if (!form.classList.contains('hidden')) {
                    form.scrollIntoView({ behavior: 'smooth' });
                }
            } else {
                console.error(`Formulář s ID delete-rights-${userId} nebyl nalezen.`);
            }
        });
    });
    
    function toggleVisibility(element) {
    if (element.classList.contains("hidden")) {
      element.classList.remove("hidden");
    } else {
      element.classList.add("hidden");
    }
    }

  setTimeout(function() {
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(function(message) {
            message.style.display = 'none';
        });
        }, 5000);
    });
function updateAccountLabel() {
  const accountLabel = document.getElementById("account-label");
  const selectedType = document.querySelector('input[name="type"]:checked').value;
  const selectedCategory = document.querySelector('select[name="category_id"]').value;

  const incomeCategories = document.querySelectorAll('.income-category');
  const outcomeCategories = document.querySelectorAll('.outcome-category');

  incomeCategories.forEach(category => category.style.display = 'none');
  outcomeCategories.forEach(category => category.style.display = 'none');

  if (selectedType === "income") {
    incomeCategories.forEach(category => category.style.display = 'block');
    accountLabel.innerHTML = '';
  } else if (selectedType === "outcome") {
    outcomeCategories.forEach(category => category.style.display = 'block');
    accountLabel.innerHTML = '';
    if (selectedCategory == "9") {
      accountLabel.innerHTML = `
        <label>Account To: 
          <input type="text" name="to_account_name" placeholder="Name of destination account" required>
        </label>`;
    }
  }
}
