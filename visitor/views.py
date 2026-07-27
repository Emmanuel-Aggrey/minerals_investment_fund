import html
import io
import zipfile
from xml.sax.saxutils import escape

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from accounts.models import Department
from .models import Staff, Visitor


def role_required(permission_name):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if (
                request.user.is_authenticated
                and getattr(request.user, permission_name, False)
            ):
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden('You do not have permission to access this page.')
        return wrapper
    return decorator


def is_admin(user):
    return user.is_authenticated and user.can_access_admin


def scoped_visitors(request):
    qs = Visitor.objects.select_related(
        'registered_by',
        'department',
        'staff_to_visit',
        'staff_to_visit__department',
        'staff_to_visit__user',
    ).all()
    if is_admin(request.user) or not request.user.is_authenticated:
        return qs
    return qs.filter(registered_by=request.user)


def filtered_visitors(request):
    qs = scoped_visitors(request)
    query = request.GET.get('q', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    purpose = request.GET.get('purpose', '').strip()
    department = request.GET.get('department', '').strip()
    status = request.GET.get('status', '').strip()

    if query:
        qs = qs.filter(
            Q(full_name__icontains=query)
            | Q(reference_number__icontains=query)
            | Q(person_to_visit__icontains=query)
            | Q(staff_to_visit__first_name__icontains=query)
            | Q(staff_to_visit__last_name__icontains=query)
            | Q(staff_to_visit__user__first_name__icontains=query)
            | Q(staff_to_visit__user__last_name__icontains=query)
            | Q(staff_to_visit__user__email__icontains=query)
        )
    if date_from:
        qs = qs.filter(visit_date__gte=date_from)
    if date_to:
        qs = qs.filter(visit_date__lte=date_to)
    if purpose:
        qs = qs.filter(purpose=purpose)
    if department:
        qs = qs.filter(department_id=department)
    if status == 'checked_in':
        qs = qs.filter(exit_time__isnull=True)
    if status == 'checked_out':
        qs = qs.filter(exit_time__isnull=False)

    return qs.distinct()


@login_required
@role_required('can_view_dashboard')
def dashboard(request):
    today = timezone.localdate()
    qs = scoped_visitors(request)
    visitors_today = qs.filter(visit_date=today)
    checked_in = qs.filter(exit_time__isnull=True)
    checked_out_today = visitors_today.filter(exit_time__isnull=False)
    month_visits = qs.filter(
        visit_date__year=today.year,
        visit_date__month=today.month,
    )
    recent_limit = 20 if is_admin(request.user) else 10
    purpose_breakdown = month_visits.values('purpose').annotate(
        total=Count('id')
    ).order_by('-total')
    department_breakdown = month_visits.values('department__name').annotate(
        total=Count('id')
    ).order_by('-total')

    most_active = None
    if is_admin(request.user):
        most_active = month_visits.values(
            'registered_by__first_name',
            'registered_by__last_name',
            'registered_by__email',
        ).annotate(total=Count('id')).order_by('-total').first()

    return render(request, 'dashboard.html', {
        'total_today': visitors_today.count(),
        'total_month': month_visits.count(),
        'checked_in': checked_in.count(),
        'checked_out': checked_out_today.count(),
        'recent': qs[:recent_limit],
        'purpose_breakdown': purpose_breakdown,
        'department_breakdown': department_breakdown,
        'most_active': most_active,
        'is_admin_view': is_admin(request.user),
    })


@login_required
@role_required('can_register_visit')
def register_visitor(request):
    if request.method == 'POST':
        data = request.POST
        consent = data.get('consent_given') == 'on'
        if not consent:
            messages.error(
                request, 'Visitor must consent before registration.')
            return render(request, 'register.html', form_context(data))

        staff_id = data.get('staff_to_visit') or None
        manual_person = data.get('person_to_visit', '').strip()
        if bool(staff_id) == bool(manual_person):
            messages.error(
                request,
                'Choose a staff member or enter a person to visit, not both.',
            )
            return render(request, 'register.html', form_context(data))

        staff = None
        department_id = data.get('department') or None
        if staff_id:
            staff = get_object_or_404(
                Staff.objects.select_related('department', 'user'),
                pk=staff_id,
            )
            department_id = staff.department_id

        visitor = Visitor(
            full_name=data.get('full_name', '').strip(),
            phone=data.get('phone', '').strip(),
            email=data.get('email') or None,
            person_to_visit=manual_person,
            staff_to_visit=staff,
            department_id=department_id,
            purpose=data.get('purpose'),
            expected_duration=data.get('expected_duration', ''),
            notes=data.get('notes', '').strip(),
            consent_given=True,
            registered_by=request.user if request.user.is_authenticated else None,
        )
        try:
            visitor.full_clean()
        except ValidationError as exc:
            for error in exc.messages:
                messages.error(request, error)
            return render(request, 'register.html', form_context(data))
        visitor.save()
        return redirect('visitor_confirm', pk=visitor.pk)

    return render(request, 'register.html', form_context())


def form_context(data=None):
    return {
        'data': data or {},
        'purposes': Visitor.PURPOSE_CHOICES,
        'durations': Visitor.DURATION_CHOICES,
        'departments': Department.objects.order_by('name'),
        'staff_members': Staff.objects.select_related(
            'department', 'user'
        ).order_by('user__first_name', 'user__last_name', 'first_name', 'last_name'),
    }


@login_required
@role_required('can_register_visit')
def visitor_confirm(request, pk):
    visitor = get_object_or_404(scoped_visitors(request), pk=pk)
    return render(request, 'confirm.html', {'visitor': visitor})


def visitor_detail(request, pk):
    if not (
        request.user.is_authenticated and (
            request.user.can_view_dashboard
            or request.user.can_register_visit
            or request.user.can_view_reports
        )
    ):
        return HttpResponseForbidden('You do not have permission to access this page.')
    visitor = get_object_or_404(scoped_visitors(request), pk=pk)
    return render(request, 'detail.html', {'visitor': visitor})


@login_required
@role_required('can_register_visit')
def record_exit(request, pk):
    visitor = get_object_or_404(scoped_visitors(request), pk=pk)
    if request.method == 'POST':
        now = timezone.now()
        if visitor.entry_time and now < visitor.entry_time:
            messages.error(request, 'Exit time cannot be before entry time.')
        elif visitor.exit_time:
            messages.info(request, 'Exit time has already been recorded.')
        else:
            visitor.exit_time = now
            visitor.save(update_fields=['exit_time'])
            messages.success(request, 'Exit time recorded.')
        return redirect('visitor_detail', pk=pk)
    return render(request, 'exit.html', {'visitor': visitor})


@login_required
@role_required('can_view_reports')
def reports(request):
    records = filtered_visitors(request)
    return render(request, 'reports.html', {
        'records': records[:200],
        'total_records': records.count(),
        'purposes': Visitor.PURPOSE_CHOICES,
        'departments': Department.objects.order_by('name'),
        'filters': request.GET,
    })


def report_rows(request):
    rows = []
    for visitor in filtered_visitors(request):
        rows.append([
            visitor.reference_number,
            visitor.full_name,
            visitor.phone,
            person_visited_name(visitor),
            visitor.department_name,
            visitor.purpose,
            local_dt(visitor.entry_time),
            local_dt(
                visitor.exit_time) if visitor.exit_time else 'Still checked in',
            visitor.duration or 'In progress',
            officer_name(visitor),
        ])
    return rows


def officer_name(visitor):
    user = visitor.registered_by
    if not user:
        return 'Unassigned'
    return getattr(user, 'full_name', '') or user.email


def person_visited_name(visitor):
    return visitor.person_visited_name or 'N/A'


def local_dt(value):
    return timezone.localtime(value).strftime('%Y-%m-%d %H:%M')


@login_required
@role_required('can_view_reports')
def export_excel(request):
    headers = [
        'Reference No.', 'Visitor Name', 'Phone', 'Person Visited',
        'Department', 'Purpose', 'Entry Time', 'Exit Time', 'Duration',
        'Registered By',
    ]
    rows = [headers, *report_rows(request)]
    content = build_xlsx(rows)
    response = HttpResponse(
        content,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="miif-visitor-report.xlsx"'
    return response


@login_required
@role_required('can_view_reports')
def export_pdf(request):
    rows = report_rows(request)
    lines = [
        'MINERALS INCOME INVESTMENT FUND',
        'Visitor Management Report',
        f'Generated: {timezone.localtime().strftime("%Y-%m-%d %H:%M")}',
        f'Total records: {len(rows)}',
        '',
    ]
    for row in rows:
        lines.append(
            f'{row[0]} | {row[1]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]}'
        )
    content = build_simple_pdf(lines)
    response = HttpResponse(content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="miif-visitor-report.pdf"'
    return response


def build_xlsx(rows):
    sheet_rows = []
    for row_number, row in enumerate(rows, start=1):
        cells = []
        for column_number, value in enumerate(row, start=1):
            ref = f'{xlsx_col(column_number)}{row_number}'
            style = ' s="1"' if row_number == 1 else ''
            cells.append(
                f'<c r="{ref}" t="inlineStr"{style}><is><t>{escape(str(value))}</t></is></c>'
            )
        sheet_rows.append(f'<row r="{row_number}">{"".join(cells)}</row>')

    worksheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" '
        'activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
        f'<sheetData>{"".join(sheet_rows)}</sheetData>'
        f'<autoFilter ref="A1:J{max(len(rows), 1)}"/></worksheet>'
    )
    files = {
        '[Content_Types].xml': '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        '</Types>',
        '_rels/.rels': '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>',
        'xl/workbook.xml': '<?xml version="1.0" encoding="UTF-8"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Visitor Report" sheetId="1" r:id="rId1"/></sheets></workbook>',
        'xl/_rels/workbook.xml.rels': '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        '</Relationships>',
        'xl/styles.xml': '<?xml version="1.0" encoding="UTF-8"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="2"><font/><font><b/></font></fonts>'
        '<fills count="1"><fill><patternFill patternType="none"/></fill></fills>'
        '<borders count="1"><border/></borders>'
        '<cellStyleXfs count="1"><xf fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="2"><xf fontId="0" fillId="0" borderId="0" xfId="0"/>'
        '<xf fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs>'
        '</styleSheet>',
        'xl/worksheets/sheet1.xml': worksheet,
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path, data in files.items():
            archive.writestr(path, data)
    return output.getvalue()


def xlsx_col(number):
    name = ''
    while number:
        number, remainder = divmod(number - 1, 26)
        name = chr(65 + remainder) + name
    return name


def build_simple_pdf(lines):
    stream_lines = ['BT', '/F1 10 Tf', '50 790 Td', '14 TL']
    for line in lines[:48]:
        escaped = html.escape(line, quote=False).replace(
            '\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        stream_lines.append(f'({escaped[:120]}) Tj')
        stream_lines.append('T*')
    stream_lines.append('ET')
    stream = '\n'.join(stream_lines).encode()
    objects = [
        b'<< /Type /Catalog /Pages 2 0 R >>',
        b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
        b'<< /Length ' + str(len(stream)).encode() +
        b' >>\nstream\n' + stream + b'\nendstream',
    ]
    pdf = io.BytesIO()
    pdf.write(b'%PDF-1.4\n')
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(pdf.tell())
        pdf.write(f'{index} 0 obj\n'.encode() + obj + b'\nendobj\n')
    xref = pdf.tell()
    pdf.write(f'xref\n0 {len(objects) + 1}\n0000000000 65535 f \n'.encode())
    for offset in offsets[1:]:
        pdf.write(f'{offset:010d} 00000 n \n'.encode())
    pdf.write(
        f'trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF'.encode()
    )
    return pdf.getvalue()
