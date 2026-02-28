import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
import paths_dir
import test_evaluator

matplotlib.use('Agg')

def create_audiogram_image(ear_data, ear_side, patient_name, output_path):
    frequencies = [125, 250, 500, 1000, 2000, 3000, 4000, 6000, 8000]
    frequency_labels = ['125', '250', '500', '1K', '2K', '3K', '4K', '6K', '8K']
    
    threshold_values = []
    for freq in frequencies:
        if freq in ear_data:
            threshold_values.append(ear_data[freq])
        else:
            threshold_values.append(None)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    ax.set_xlim(0, len(frequencies) - 1)
    ax.set_ylim(-10, 120)
    ax.invert_yaxis()
    
    ax.set_xticks(range(len(frequencies)))
    ax.set_xticklabels(frequency_labels, fontsize=12)
    ax.set_xlabel('Frequenz (Hz)', fontsize=14, fontweight='bold')
    
    ax.set_yticks(range(-10, 121, 10))
    ax.set_ylabel('Hörschwelle (Dezibel)', fontsize=14, fontweight='bold')
    
    ax.grid(True, alpha=0.3, linewidth=0.5)
    ax.set_facecolor('#f5f5f5')
    
    green_zone = Polygon([(0, -10), (len(frequencies)-1, -10), 
                          (len(frequencies)-1, 25), (0, 25)], 
                         facecolor='lightgreen', alpha=0.3, edgecolor='none')
    ax.add_patch(green_zone)
    
    yellow_zone = Polygon([(0, 25), (len(frequencies)-1, 25), 
                           (len(frequencies)-1, 40), (0, 40)], 
                          facecolor='yellow', alpha=0.3, edgecolor='none')
    ax.add_patch(yellow_zone)
    
    red_zone = Polygon([(0, 40), (len(frequencies)-1, 40), 
                        (len(frequencies)-1, 120), (0, 120)], 
                       facecolor='lightcoral', alpha=0.3, edgecolor='none')
    ax.add_patch(red_zone)
    
    valid_indices = []
    valid_values = []
    for i, val in enumerate(threshold_values):
        if val is not None:
            valid_indices.append(i)
            valid_values.append(val)
    
    if valid_indices:
        marker_style = 'o' if ear_side == 'right' else 'x'
        marker_color = 'red' if ear_side == 'right' else 'blue'
        marker_size = 12
        
        ax.plot(valid_indices, valid_values, 
                marker=marker_style, 
                color=marker_color,
                linewidth=2, 
                markersize=marker_size,
                label=f'{ear_side.capitalize()} Ohr')
    
    title = f'Audiogramm - {ear_side.upper()} Ohr'
    if patient_name:
        title += f'\n{patient_name}'
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    ax.legend(loc='lower right', fontsize=12)
    
    ax.text(0.02, 0.98, 'Normal', transform=ax.transAxes,
            fontsize=10, verticalalignment='top', color='darkgreen', fontweight='bold')
    ax.text(0.02, 0.65, 'Leicht', transform=ax.transAxes,
            fontsize=10, verticalalignment='top', color='orange', fontweight='bold')
    ax.text(0.02, 0.45, 'Schwer', transform=ax.transAxes,
            fontsize=10, verticalalignment='top', color='darkred', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return output_path

def create_pdf_report(patient_data, evaluation_results, output_filename):
    paths_dir.SAVED_TESTS_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = paths_dir.SAVED_TESTS_DIR / output_filename
    
    temp_dir = paths_dir.SAVED_TESTS_DIR / "temp_images"
    temp_dir.mkdir(exist_ok=True)
    
    patient_info = patient_data['patient_info']
    patient_name = patient_info.get('name', 'Unbekannt')
    
    left_image_path = temp_dir / "left_audiogram.png"
    right_image_path = temp_dir / "right_audiogram.png"
    
    create_audiogram_image(patient_data['left_ear'], 'linkes', patient_name, left_image_path)
    create_audiogram_image(patient_data['right_ear'], 'rechtes', patient_name, right_image_path)
    
    pdf_canvas = canvas.Canvas(str(pdf_path), pagesize=A4)
    page_width, page_height = A4
    
    pdf_canvas.setFont("Helvetica-Bold", 20)
    pdf_canvas.drawString(2*cm, page_height - 2*cm, "Hörtest Ergebnis")
    
    pdf_canvas.setFont("Helvetica", 12)
    y_position = page_height - 3*cm
    
    pdf_canvas.drawString(2*cm, y_position, f"Patient: {patient_name}")
    y_position -= 0.6*cm
    
    if patient_info.get('birthdate'):
        birthdate = datetime.strptime(patient_info['birthdate'], "%Y%m%d").strftime("%d.%m.%Y")
        pdf_canvas.drawString(2*cm, y_position, f"Geburtsdatum: {birthdate}")
        y_position -= 0.6*cm
    
    if patient_info.get('exam_date'):
        pdf_canvas.drawString(2*cm, y_position, f"Testdatum: {patient_info['exam_date']}")
        y_position -= 0.6*cm
    
    pdf_canvas.drawString(2*cm, y_position, f"Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    y_position -= 1.2*cm
    
    pdf_canvas.setFont("Helvetica-Bold", 14)
    pdf_canvas.drawString(2*cm, y_position, "Bewertung:")
    y_position -= 0.8*cm
    
    pdf_canvas.setFont("Helvetica", 11)
    
    left_color = evaluation_results['left']['color']
    left_warning = evaluation_results['left']['high_freq_warning']
    
    left_status_text = {
        'green': 'Normal',
        'yellow': 'Leichte Auffälligkeit',
        'red': 'Deutliche Hörminderung'
    }[left_color]
    
    pdf_canvas.drawString(2*cm, y_position, f"Linkes Ohr: {left_status_text}")
    if left_warning:
        pdf_canvas.drawString(4*cm, y_position - 0.5*cm, "⚠ Hochtonverlust erkannt")
        y_position -= 0.5*cm
    y_position -= 0.8*cm
    
    right_color = evaluation_results['right']['color']
    right_warning = evaluation_results['right']['high_freq_warning']
    
    right_status_text = {
        'green': 'Normal',
        'yellow': 'Leichte Auffälligkeit',
        'red': 'Deutliche Hörminderung'
    }[right_color]
    
    pdf_canvas.drawString(2*cm, y_position, f"Rechtes Ohr: {right_status_text}")
    if right_warning:
        pdf_canvas.drawString(4*cm, y_position - 0.5*cm, "⚠ Hochtonverlust erkannt")
        y_position -= 0.5*cm
    y_position -= 1.5*cm
    
    pdf_canvas.setFont("Helvetica-Bold", 14)
    pdf_canvas.drawString(2*cm, y_position, "Audiogramme:")
    y_position -= 0.5*cm
    
    image_width = 16*cm
    image_height = 12*cm
    
    pdf_canvas.drawImage(str(left_image_path), 
                        2*cm, y_position - image_height,
                        width=image_width, height=image_height)
    
    pdf_canvas.showPage()
    
    pdf_canvas.setFont("Helvetica-Bold", 20)
    pdf_canvas.drawString(2*cm, page_height - 2*cm, "Hörtest Ergebnis (Fortsetzung)")
    
    y_position = page_height - 3*cm
    
    pdf_canvas.drawImage(str(right_image_path), 
                        2*cm, y_position - image_height,
                        width=image_width, height=image_height)
    
    y_position -= image_height + 1*cm
    
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(2*cm, y_position, "Empfehlung:")
    y_position -= 0.6*cm
    
    pdf_canvas.setFont("Helvetica", 10)
    
    worst_result = 'red' if (left_color == 'red' or right_color == 'red') else \
                   'yellow' if (left_color == 'yellow' or right_color == 'yellow') else 'green'
    
    if worst_result == 'red':
        recommendation = "Bitte vereinbaren Sie zeitnah einen Termin bei einem HNO-Arzt."
    elif worst_result == 'yellow':
        recommendation = "Wir empfehlen eine HNO-ärztliche Kontrolle."
    else:
        recommendation = "Ihr Hörvermögen liegt im Normalbereich. Regelmäßige Kontrollen werden empfohlen."
    
    pdf_canvas.drawString(2*cm, y_position, recommendation)
    
    pdf_canvas.save()
    
    left_image_path.unlink()
    right_image_path.unlink()
    temp_dir.rmdir()
    
    return pdf_path

def generate_report_for_patient(xml_path, config):
    
    patient_data = test_evaluator.read_patient_xml(xml_path)
    evaluation_results = test_evaluator.evaluate_patient(patient_data, config)
    
    patient_name = patient_data['patient_info'].get('name', 'Unknown').replace(' ', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pdf_filename = f"Hörtest_{patient_name}_{timestamp}.pdf"
    
    pdf_path = create_pdf_report(patient_data, evaluation_results, pdf_filename)
    
    return pdf_path