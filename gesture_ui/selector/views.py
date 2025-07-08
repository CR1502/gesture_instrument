from django.shortcuts import render, redirect
from .forms import InstrumentSelectionForm, INSTRUMENT_CHOICES
import json
import os


def instrument_selector(request):
    if request.method == 'POST':
        form = InstrumentSelectionForm(request.POST)
        if form.is_valid():
            left_instrument = form.cleaned_data["left_instrument"]
            right_instrument = form.cleaned_data["right_instrument"]

            # Save to session (for internal Django use if needed)
            request.session['left_instrument'] = left_instrument
            request.session['right_instrument'] = right_instrument

            # ✅ Save to JSON at project root (same directory as main.py)
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            json_path = os.path.join(project_root, 'instrument_selection.json')

            selection = {
                "left_instrument": int(left_instrument),
                "right_instrument": int(right_instrument)
            }

            with open(json_path, 'w') as f:
                json.dump(selection, f)

            # ✅ Convert instrument numbers to human-readable names
            instrument_dict = dict(INSTRUMENT_CHOICES)
            left_name = instrument_dict.get(int(left_instrument), "Unknown")
            right_name = instrument_dict.get(int(right_instrument), "Unknown")

            # ✅ Show success page with instrument names
            return render(request, 'selector/success.html', {
                'left_name': left_name,
                'right_name': right_name
            })

    else:
        form = InstrumentSelectionForm()

    return render(request, 'selector/instrument_selector.html', {'form': form})