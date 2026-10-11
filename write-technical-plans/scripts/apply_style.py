#!/usr/bin/env python3
"""Apply the editable technical-plan style to a DOCX without rewriting text.

Dependency: lxml. Run with --help for the CLI. Uses assets/style.json by default.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
NS = {'w': W, 'a': A}
TABLE_STYLES = ('three_line', 'grid', 'matrix', 'schedule', 'plain', 'preserve')
TABLE_STYLE_IDS = {'plan' + name.replace('_', ''): name for name in TABLE_STYLES}
TABLE_MARKER = re.compile(r'^\[plan-table:([a-z_]+);headers=(\d+)\](?: )?')
TABLE_BORDER_SIDES = ('top', 'left', 'start', 'bottom', 'right', 'end', 'insideH', 'insideV')


def q(name):
    return '{' + W + '}' + name


def ensure(parent, name):
    node = parent.find(q(name))
    if node is None:
        node = etree.SubElement(parent, q(name))
    return node


def assign(parent, name, values):
    node = ensure(parent, name)
    node.attrib.clear()
    for key, value in values.items():
        node.set(q(key), str(value))
    return node


def font(pr, size, profile, heading=False):
    f = profile['fonts']
    assign(pr, 'rFonts', {'ascii': f['latin'], 'hAnsi': f['latin'],
                          'cs': f['latin'], 'eastAsia': f['heading_cjk'] if heading else f['body_cjk']})
    assign(pr, 'color', {'val': f['text_color']})
    for name in ['sz', 'szCs']:
        assign(pr, name, {'val': round(size * 2)})


def role(style_id):
    key = re.sub(r'\s+', '', style_id.casefold())
    if key == 'title' or key == 'titlechar': return 'title'
    if key == 'subtitle' or key == 'subtitlechar': return 'subtitle'
    for level in range(1, 4):
        if key.startswith('heading' + str(level)): return 'heading' + str(level)
    if key in ['planmetadata', 'metadata']: return 'metadata'
    if key in ['planreference', 'bibliography']: return 'reference'
    if key == 'plantablecaption': return 'table_caption'
    if key == 'planfigurecaption': return 'figure_caption'
    if 'caption' in key: return 'caption'
    if key in ['header', 'footer']: return 'reference'
    if 'list' in key or 'code' in key: return 'list'
    return 'body'


def style_role(style):
    """Use a style's semantic name when Word assigns an opaque style ID."""
    name = style.find('w:name', NS)
    named_role = role(name.get(q('val'), '')) if name is not None else 'body'
    return named_role if named_role != 'body' else role(style.get(q('styleId'), ''))


def picture_only(p):
    """Recognize picture paragraphs without changing mixed text/image content."""
    media = p.xpath('.//w:drawing | .//w:pict | .//w:object', namespaces=NS)
    text = p.xpath('.//w:t/text() | .//w:instrText/text() | .//w:delText/text()', namespaces=NS)
    return bool(media) and not any(t.strip() for t in text)


def paragraph(p, profile, style_roles, story=False):
    cfg = profile['paragraph']
    pp = ensure(p, 'pPr')
    sid = pp.find('w:pStyle', NS)
    sid = sid.get(q('val'), 'Normal') if sid is not None else 'Normal'
    kind = style_roles.get(sid, role(sid))
    text = ''.join(p.xpath('.//w:t/text()', namespaces=NS)).strip()
    cell = any(a.tag == q('tc') for a in p.iterancestors())
    image = picture_only(p)
    if cell: kind = 'table'
    elif story: kind = 'reference'
    elif kind == 'body' and (re.match(r'^\[\d+\]', text) or text.startswith(('http://', 'https://'))): kind = 'reference'
    elif kind == 'body' and text.startswith('编制日期'): kind = 'metadata'
    elif kind == 'body' and pp.find('w:numPr', NS) is not None: kind = 'list'
    size = cfg.get(kind + '_pt', cfg.get('caption_pt', cfg['body_pt']) if kind.endswith('_caption') else cfg['body_pt'])
    line, before, after = cfg['body_line_spacing'], 0, cfg['body_space_after_pt']
    if kind == 'table':
        size = profile['table']['font_pt']
        line, after = profile['table']['line_spacing'], profile['table']['space_after_pt']
    elif kind.startswith('heading'):
        line, before, after = cfg['heading_line_spacing'], cfg['heading_space_before_pt'], cfg['heading_space_after_pt']
        assign(pp, 'keepNext', {'val': 1})
    elif kind == 'title':
        line, after = cfg['title_line_spacing'], cfg['title_space_after_pt']
        assign(pp, 'keepNext', {'val': 1})
    elif kind in ['reference', 'metadata', 'caption', 'table_caption', 'figure_caption', 'subtitle']:
        line, after = cfg.get('secondary_line_spacing', cfg['heading_line_spacing']), cfg.get('secondary_space_after_pt', profile['table']['space_after_pt'])
        if kind in ['caption', 'table_caption', 'figure_caption']:
            assign(pp, 'keepNext', {'val': int(kind == 'table_caption')})
        elif kind == 'subtitle': assign(pp, 'keepNext', {'val': 1})
    ind = ensure(pp, 'ind')
    for key in ['firstLineChars', 'hanging', 'hangingChars']:
        ind.attrib.pop(q(key), None)
    first = size * cfg['first_line_characters'] if kind == 'body' and text and not image else 0
    ind.set(q('firstLine'), str(round(first * 20)))
    assign(pp, 'spacing', {'line': round(line * 240), 'lineRule': 'auto',
                           'before': round(before * 20), 'after': round(after * 20)})
    if image:
        assign(pp, 'jc', {'val': cfg.get('picture_alignment', 'center')})
        assign(pp, 'keepNext', {'val': 1})
    elif kind == 'body': assign(pp, 'jc', {'val': cfg['body_alignment']})
    assign(pp, 'widowControl', {'val': 1})
    for node in pp.findall('w:pBdr', NS): pp.remove(node)
    heading = kind.startswith('heading') or kind in ['title', 'subtitle']
    font(ensure(pp, 'rPr'), size, profile, heading)
    for r in p.findall('.//w:r', NS): font(ensure(r, 'rPr'), size, profile, heading)


def border(pr, name, profile, thickness=None):
    val = {'val': 'nil'} if thickness is None else {
        'val': 'single', 'sz': round(thickness * 8), 'color': profile['table']['rule_color'], 'space': 0}
    assign(pr, name, val)


def table_xml(table):
    node = getattr(table, '_tbl', table)
    if not isinstance(node, etree._Element) or node.tag != q('tbl'):
        raise TypeError('Expected a python-docx Table or a w:tbl XML element.')
    return node


def mark_table(table, style, header_rows=1):
    """Mark a python-docx Table or w:tbl element, preserving its alt description.

    style is one of TABLE_STYLES; header_rows is a nonnegative integer. The
    returned value is the original object. Repeated calls replace the prefix.
    """
    if style not in TABLE_STYLES:
        raise ValueError('Unknown table style: ' + str(style))
    if isinstance(header_rows, bool) or not isinstance(header_rows, int) or header_rows < 0:
        raise ValueError('header_rows must be a nonnegative integer.')
    node = table_xml(table)
    pr = ensure(node, 'tblPr')
    description = ensure(pr, 'tblDescription')
    suffix = description.get(q('val'), '')
    while TABLE_MARKER.match(suffix):
        suffix = TABLE_MARKER.sub('', suffix, count=1)
    description.set(q('val'), f'[plan-table:{style};headers={header_rows}]' + (' ' + suffix if suffix else ''))
    order_properties(node)
    return table


def image_layout_only(table):
    """A borderless layout exception contains images and no textual content."""
    media = etree.XPath('.//w:drawing | .//w:pict | .//w:object', namespaces=NS)(table)
    text = etree.XPath('.//w:t/text() | .//w:instrText/text() | .//w:delText/text()', namespaces=NS)(table)
    return bool(media) and not any(t.strip() for t in text)


def table_choice(table, profile):
    cfg = profile['table']
    pr = table.find('w:tblPr', NS)
    headers = cfg.get('header_rows', 1)
    if isinstance(headers, bool) or not isinstance(headers, int) or headers < 0:
        raise ValueError('table.header_rows must be a nonnegative integer.')
    force = cfg.get('force_content_three_line', False)
    if not isinstance(force, bool):
        raise ValueError('table.force_content_three_line must be a boolean.')

    def choice(style, count):
        if force:
            if style == 'plain' and image_layout_only(table): return 'plain', 0
            return 'three_line', count
        return style, count

    if pr is not None:
        description = pr.find('w:tblDescription', NS)
        marker = TABLE_MARKER.match(description.get(q('val'), '')) if description is not None else None
        if marker and marker.group(1) in TABLE_STYLES:
            return choice(marker.group(1), int(marker.group(2)))
        if force:
            existing_headers = 0
            for row in table.findall('w:tr', NS):
                repeat = row.find('w:trPr/w:tblHeader', NS)
                if repeat is None or repeat.get(q('val'), '1') in ('0', 'false', 'off'): break
                existing_headers += 1
            if existing_headers: headers = existing_headers
        sid = pr.find('w:tblStyle', NS)
        sid = sid.get(q('val'), '') if sid is not None else ''
        named = TABLE_STYLE_IDS.get(sid.lower().replace(' ', ''))
        if named: return choice(named, headers)
    else:
        sid = ''
    if force: return 'three_line', headers
    # Legacy profiles deliberately retain their original three-line default.
    default = cfg.get('default_style', 'three_line')
    if default != 'auto':
        if default not in TABLE_STYLES: raise ValueError('Unknown table.default_style: ' + str(default))
        return default, headers
    if sid.lower().replace(' ', '') == 'tablegrid': return 'grid', headers
    if sid or table.find('w:tblPr/w:tblBorders', NS) is not None:
        return 'preserve', headers
    if etree.XPath('./w:tr/w:tblPrEx/w:tblBorders | ./w:tr/w:tc/w:tcPr/w:tcBorders', namespaces=NS)(table):
        return 'preserve', headers
    return 'three_line', headers


def table_style(table, profile):
    cfg = profile['table']
    style, headers = table_choice(table, profile)
    # Recording auto choices prevents generated borders from changing a later
    # pass to preserve. The description's original accessible text survives.
    mark_table(table, style, headers)
    if style == 'preserve': return
    pr = ensure(table, 'tblPr')
    for node in pr.findall('w:tblStyle', NS): pr.remove(node)
    for node in pr.findall('w:shd', NS): pr.remove(node)
    if style in ('three_line', 'plain'):
        assign(pr, 'tblCellSpacing', {'w': 0, 'type': 'dxa'})
    bounds = ensure(pr, 'tblBorders')
    bounds.clear()
    for name in TABLE_BORDER_SIDES:
        thickness = None
        if style == 'three_line' and name in ['top', 'bottom']: thickness = cfg['outer_rule_pt']
        elif style in ['grid', 'matrix', 'schedule']: thickness = cfg.get('grid_rule_pt', cfg['header_rule_pt'])
        border(bounds, name, profile, thickness)
    assign(pr, 'tblLook', {'val': '0600', 'firstRow': 0, 'lastRow': 0, 'firstColumn': 0,
                          'lastColumn': 0, 'noHBand': 1, 'noVBand': 1})
    rows = table.findall('w:tr', NS)
    headers = min(headers, len(rows))
    for i, row in enumerate(rows):
        # Old row-level grid exceptions can override the new table borders.
        exception = row.find('w:tblPrEx', NS)
        if exception is not None:
            for name in ('tblStyle', 'tblBorders', 'shd', 'tblCellSpacing'):
                for node in exception.findall(q(name)): exception.remove(node)
            if not len(exception) and not exception.attrib: row.remove(exception)
        rp = ensure(row, 'trPr')
        if style in ('three_line', 'plain'):
            for node in rp.findall('w:tblCellSpacing', NS): rp.remove(node)
        for n in rp.findall('w:trHeight', NS): rp.remove(n)
        assign(rp, 'cantSplit', {'val': int(not cfg['allow_row_split'])})
        for n in rp.findall('w:tblHeader', NS): rp.remove(n)
        header = i < headers
        if header and cfg['repeat_header'] and style != 'plain': assign(rp, 'tblHeader', {'val': 1})
        for j, cell in enumerate(row.findall('w:tc', NS)):
            cp = ensure(cell, 'tcPr')
            assign(cp, 'vAlign', {'val': 'center'})
            if style == 'plain':
                for n in cp.findall('w:shd', NS): cp.remove(n)
            elif style == 'schedule' and not header:
                pass  # Body shading is user-authored progress-bar data.
            else:
                shade = cfg['fill']
                if style in ['grid', 'matrix', 'schedule'] and header:
                    shade = cfg.get('header_fill', cfg['fill'])
                elif style == 'matrix' and j == 0:
                    shade = cfg.get('first_column_fill', cfg.get('header_fill', cfg['fill']))
                assign(cp, 'shd', {'val': 'clear', 'fill': shade})
            for n in cp.findall('w:noWrap', NS): cp.remove(n)
            margins = ensure(cp, 'tcMar')
            for side in ['top', 'left', 'bottom', 'right']:
                assign(margins, side, {'w': round(cfg['cell_padding_pt'] * 20), 'type': 'dxa'})
            bounds = ensure(cp, 'tcBorders')
            bounds.clear()
            for side in TABLE_BORDER_SIDES:
                border(bounds, side, profile, cfg.get('grid_rule_pt', cfg['header_rule_pt']) if style in ['grid', 'matrix', 'schedule'] else None)
            if style == 'three_line' and i == 0:
                border(bounds, 'top', profile, cfg['outer_rule_pt'])
            if style == 'three_line' and headers and i == headers - 1:
                border(bounds, 'bottom', profile, cfg['header_rule_pt'])
            if header or (style == 'matrix' and j == 0):
                for p in cell.findall('w:p', NS):
                    if style != 'plain': assign(ensure(p, 'pPr'), 'jc', {'val': cfg.get('header_alignment', 'center')})
                    if header:
                        for r in p.findall('.//w:r', NS):
                            for name in ['b', 'bCs']: assign(ensure(r, 'rPr'), name, {'val': int(cfg['header_bold'] and style != 'plain')})
            if style == 'three_line' and i == len(rows) - 1: border(bounds, 'bottom', profile, cfg['outer_rule_pt'])


# OOXML properties must precede text, otherwise some Word renderers ignore them.
ORDERS = {
    'rPr': 'rStyle rFonts b bCs i iCs caps smallCaps strike dstrike outline shadow emboss imprint noProof snapToGrid vanish webHidden color spacing w kern position sz szCs highlight u effect bdr shd fitText vertAlign rtl cs em lang eastAsianLayout specVanish oMath rPrChange',
    'pPr': 'pStyle keepNext keepLines pageBreakBefore framePr widowControl numPr suppressLineNumbers pBdr shd tabs suppressAutoHyphens kinsoku wordWrap overflowPunct topLinePunct autoSpaceDE autoSpaceDN bidi adjustRightInd snapToGrid spacing ind contextualSpacing mirrorIndents suppressOverlap jc textDirection textAlignment textboxTightWrap outlineLvl divId cnfStyle rPr sectPr pPrChange',
    'tcPr': 'cnfStyle tcW gridSpan hMerge vMerge tcBorders shd noWrap tcMar textDirection tcFitText vAlign hideMark headers cellIns cellDel cellMerge tcPrChange',
    'tblPr': 'tblStyle tblpPr tblOverlap bidiVisual tblStyleRowBandSize tblStyleColBandSize tblW jc tblCellSpacing tblInd tblBorders shd tblLayout tblCellMar tblLook tblCaption tblDescription tblPrChange',
    'trPr': 'cnfStyle divId gridBefore gridAfter wBefore wAfter cantSplit trHeight tblHeader tblCellSpacing jc hidden ins del trPrChange',
    'tblBorders': 'top left start bottom right end insideH insideV',
    'tcBorders': 'top left start bottom right end insideH insideV tl2br tr2bl',
}


def order_properties(root):
    # Take snapshots: moving a property during a live iter() can skip its own
    # children and cause a second application to reorder the document again.
    for parent in list(root.iter()):
        for owner, prop in [('p', 'pPr'), ('r', 'rPr'), ('tc', 'tcPr'), ('tbl', 'tblPr'), ('tr', 'trPr')]:
            if parent.tag == q(owner):
                node = parent.find(q(prop))
                if node is not None:
                    parent.remove(node)
                    index = 0
                    if owner == 'tr':
                        exception = parent.find(q('tblPrEx'))
                        if exception is not None:
                            parent.remove(exception)
                            parent.insert(0, exception)
                            index = 1
                    parent.insert(index, node)
    for parent in list(root.iter()):
        tag = etree.QName(parent).localname
        if tag in ORDERS:
            ranks = {q(n): i for i, n in enumerate(ORDERS[tag].split())}
            parent[:] = sorted(parent, key=lambda n: ranks.get(n.tag, 999))


def signature(parts):
    return [(n, tuple(etree.fromstring(data).xpath('//*[local-name()="t"]/text()')))
            for n, data in sorted(parts.items())
            if n.startswith('word/') and n.endswith('.xml') and not n.startswith('word/styles')]


def apply(source, output, profile):
    if source.resolve() == output.resolve():
        raise ValueError('Use a different output path to keep the source intact.')
    with ZipFile(source) as archive:
        infos = archive.infolist()
        parts = {i.filename: archive.read(i.filename) for i in infos}
    old_signature = signature(parts)
    styles = etree.fromstring(parts['word/styles.xml'])
    roles = {s.get(q('styleId')): style_role(s) for s in styles.findall('w:style', NS)}
    for name, data in list(parts.items()):
        if not (name.startswith('word/') and name.endswith('.xml')): continue
        root = etree.fromstring(data)
        for n in root.findall('.//w:color', NS):
            n.attrib.clear(); n.set(q('val'), profile['fonts']['text_color'])
        for n in root.findall('.//w:rFonts', NS):
            assign(n.getparent(), 'rFonts', {'ascii': profile['fonts']['latin'], 'hAnsi': profile['fonts']['latin'],
                                            'cs': profile['fonts']['latin'], 'eastAsia': profile['fonts']['body_cjk']})
        for s in root.findall('.//w:style', NS):
            kind = roles.get(s.get(q('styleId')), style_role(s))
            cfg = profile['paragraph']
            fallback = cfg.get('caption_pt', cfg['body_pt']) if kind.endswith('_caption') else cfg['body_pt']
            size = cfg.get(kind + '_pt', fallback)
            font(ensure(s, 'rPr'), size, profile, kind.startswith('heading') or kind in ['title', 'subtitle'])
            if kind in ['title', 'subtitle', 'heading1', 'heading2', 'heading3']:
                for n in s.findall('w:pPr/w:pBdr', NS): n.getparent().remove(n)
        if name.startswith('word/theme/'):
            for n in root.findall('.//a:fontScheme//a:latin', NS): n.set('typeface', profile['fonts']['latin'])
            for n in root.findall('.//a:fontScheme//a:ea', NS): n.set('typeface', profile['fonts']['body_cjk'])
        for p in root.findall('.//w:p', NS):
            paragraph(p, profile, roles, story=name != 'word/document.xml')
        for t in root.findall('.//w:tbl', NS): table_style(t, profile)
        if name == 'word/document.xml':
            cfg = profile['page']
            for s in root.findall('.//w:sectPr', NS):
                assign(s, 'pgSz', {'w': round(cfg['width_pt'] * 20), 'h': round(cfg['height_pt'] * 20)})
                pm = ensure(s, 'pgMar')
                for side in ['top', 'bottom', 'left', 'right']:
                    pm.set(q(side), str(round(cfg['margin_' + side + '_pt'] * 20)))
                pm.set(q('footer'), str(round(cfg['footer_distance_pt'] * 20)))
        order_properties(root)
        parts[name] = etree.tostring(root, encoding='UTF-8', xml_declaration=True, standalone=True)
    if signature(parts) != old_signature: raise ValueError('Text changed; output was not written.')
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        for info in infos: archive.writestr(info, parts[info.filename])
    return {'output': str(output.resolve()), 'text_preserved': True,
            'profile_version': profile['profile_version'], 'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--profile', type=Path, default=Path(__file__).resolve().parents[1] / 'assets/style.json')
    args = parser.parse_args()
    print(json.dumps(apply(args.source, args.output, json.loads(args.profile.read_text(encoding='utf-8'))), ensure_ascii=False))
