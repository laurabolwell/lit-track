/* jshint esversion: 11 */
document.addEventListener('DOMContentLoaded', function () {
  // sidenav for mobile initialization
  let sidenav = document.querySelectorAll('.sidenav');
  M.Sidenav.init(sidenav, { edge: "right" });
  // collapsible initialization
  let collapsible = document.querySelectorAll('.collapsible');
  M.Collapsible.init(collapsible);
  // select dropdown initialization
  let select = document.querySelectorAll('select');
  M.FormSelect.init(select);
  // datepicker initialization
  let datepicker = document.querySelectorAll('.datepicker');
  M.Datepicker.init(datepicker, {
    format: "dd mmmm, yyyy",
    yearRange: 0,
    autoClose: true,
    maxDate: new Date()
  });
  // modal initialization
  let modal = document.querySelectorAll('.modal');
  M.Modal.init(modal, {
    dismissable: false
  });
  // autocomplete for title initialization
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
  // initialization for tooltips
  let tooltipped = document.querySelectorAll('.tooltipped');
  M.Tooltip.init(tooltipped, {
  });
});