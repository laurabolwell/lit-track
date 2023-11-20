document.addEventListener('DOMContentLoaded', function () {
  let sidenav = document.querySelectorAll('.sidenav');
  M.Sidenav.init(sidenav, { edge: "right" });
  let collapsible = document.querySelectorAll('.collapsible');
  M.Collapsible.init(collapsible);
  let select = document.querySelectorAll('select');
  M.FormSelect.init(select);
  let datepicker = document.querySelectorAll('.datepicker');
  M.Datepicker.init(datepicker, {
    format: "dd mmmm, yyyy",
    yearRange: 0,
    autoClose: true,
  });
  let modal = document.querySelectorAll('.modal');
  M.Modal.init(modal, {
    dismissable: false
  });
  let autocomplete = document.querySelectorAll('.autocomplete');
  M.Autocomplete.init(autocomplete, {
    minLength: 0,
    data: [
      { id: "Mrs" },
      { id: "Mr" },
      { id: "Miss" },
      { id: "Ms" },
      { id: "Mx" },
      { id: "Dr" },
    ]
  });
  let timeleft = 10;
  let downloadTimer = setInterval(function () {
    timeleft--;
    document.getElementById("countdowntimer").textContent = timeleft;
    if (timeleft <= 0) {
      clearInterval(downloadTimer);
    }
  }, 1000);
});