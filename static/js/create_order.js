jquery(function () {
  const tileFormset = $('#tile-formset');
  const totalFormsInput = $('#id_tile_details-TOTAL_FORMS');

  // Add a new tile row
  $(document).on('click', '.add-tile-row', function () {
      const totalForms = parseInt($('#id_tile_details-TOTAL_FORMS').val());
      const lastRow = $('#tile-formset').find('.tile-row:last');
      const newRow = lastRow.clone(true);

      // Update formset indices in the new row
      updateFormIndices(newRow, totalForms);

      // Remove the "+" button from all rows and add it only to the new row
      $('#tile-formset').find('.add-tile-row').remove();
      newRow.find('td:last').html('<button type="button" class="add-tile-row" style="cursor: pointer;">+</button>');

      // Append the new row and increment TOTAL_FORMS
      $('#tile-formset').append(newRow);
      $('#id_tile_details-TOTAL_FORMS').val(totalForms + 1);

      updateSubTotal(); // Update the subtotal after adding a new row
  });

  // Fetch tile data dynamically
  $(document).on('change', '[name$="article_number"]', function () {
      const articleNumber = $(this).val();
      const row = $(this).closest('.tile-row');
      $.get('/get_tile_data/', { article_number: articleNumber }, function (data) {
          if (data) {
              row.find('[name$="category"]').val(data.category);
              row.find('[name$="description"]').val(data.description);
              row.find('[name$="tile_size"]').val(data.tile_size);
              row.find('[name$="box_size"]').val(data.box_size);
              row.find('[name$="peiece_per_box"]').val(data.peiece_per_box);
              row.find('[name$="sale_unit"]').val(data.sale_unit);
              row.find('[name$="rate"]').val(data.rate);
          }
      });
  });

  // Automatically calculate price when rate or quantity changes
  $(document).on('input', '[name$="rate"], [name$="quantity"]', function () {
      const row = $(this).closest('.tile-row');
      const rate = parseFloat(row.find('[name$="rate"]').val()) || 0;
      const quantity = parseInt(row.find('[name$="quantity"]').val()) || 0;
      const price = rate * quantity;
      row.find('.price-field').val(price.toFixed(2));

      updateSubTotal(); // Update the subtotal when a row is updated
  });

  // Function to calculate and update the subtotal
  function updateSubTotal() {
      let subTotal = 0;

      $('#tile-formset .tile-row').each(function () {
          const price = parseFloat($(this).find('.price-field').val()) || 0;
          subTotal += price;
      });

      $('#subtotal').val(subTotal.toFixed(2));
  }

  function updateFormIndices(row, newIndex) {
      row.find(':input').each(function () {
          const name = $(this).attr('name');
          const id = $(this).attr('id');

          if (name) {
              $(this).attr('name', name.replace(/-\d+-/, `-${newIndex}-`));
          }
          if (id) {
              $(this).attr('id', id.replace(/-\d+-/, `-${newIndex}-`));
          }

          // Clear input values except for management form inputs
          if (!$(this).is('[type="hidden"]')) {
              $(this).val('');
          }
      });

      // Reset price field
      row.find('.price-field').val('');
  }
});