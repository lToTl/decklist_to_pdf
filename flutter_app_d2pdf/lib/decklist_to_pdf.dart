// Translated from the original Python script to Dart (simplified)

import 'dart:convert';
import 'dart:core';
//import 'dart:ffi';
import 'dart:io';
import 'dart:typed_data';
import 'dart:math' as math;
import 'dart:collection';

import 'package:http/http.dart' as http;
import 'package:image/image.dart' as img;
import 'package:pdf/widgets.dart' as pw;
import 'package:pdf/pdf.dart' as pdf;
import 'package:path/path.dart' as p;
import 'data_service.dart';
//import 'package:hive/hive.dart' as hive;

class DecklistToPdfCore {
  final Map<String, dynamic> conf = {};
  final List<Map<String, dynamic>> decklist = [];
  final Map<String, img.Image> imageCache = {};
  late final Map<String, dynamic> consts;

  DecklistToPdfCore({Map<String, dynamic>? overrideConfig}) {
    initConfig(overrideConfig: overrideConfig);
    setupWorkspace();
  }

  int getColor(int r, int g, int b, int a) {
    return ((a & 0xFF) << 24) |
        ((r & 0xFF) << 16) |
        ((g & 0xFF) << 8) |
        ((b & 0xFF));
  }

  int getRed(int c) => (c >> 16) & 0xFF;
  int getGreen(int c) => (c >> 8) & 0xFF;
  int getBlue(int c) => c & 0xFF;
  int getAlpha(int c) => (c >> 24) & 0xFF;

  void setupWorkspace() {
    // Create necessary folders from Run.sh
    final dirs = [
      'scryfall_bulk_json',
      'cardbacks',
      'custom_cards',
      'image_cache/small',
      'image_cache/normal',
      'hive_db',
      'image_cache/large',
      'image_cache/png',
      'image_cache/art_crop',
      'image_cache/border_crop',
      'output',
      'input',
    ];
    for (final dir in dirs) {
      Directory(dir).createSync(recursive: true);
    }

    // Create the decklist file if it doesn't exist
    final decklistPath = conf['decklist_path'] as String;
    final decklistFile = File(decklistPath);
    if (!decklistFile.existsSync()) {
      const exampleDecklist = '''
1 Yahenni, Undying Partisan (CMM) 201
1 Accursed Marauder (MH3) 80
1 Animate Dead (MKC) 125
1 Blood Seeker (ZEN) 80
1 Carrier Thrall (2X2) 72
1 Cartouche of Ambition (AKH) 83
1 Creeping Bloodsucker (J22) 21
1 Crypt Rats (VIS) 55
1 Cult Conscript (DMU) 88
1 Dance of the Dead (ICE) 118
1 Deathgreeter (DDD) 33
1 Death's-Head Buzzard (VMA) 115
''';
      decklistFile.writeAsStringSync(exampleDecklist);
    }
  }

  void initConfig({Map<String, dynamic>? overrideConfig}) {
    conf.addAll({
      'decklist_path': 'decklist.txt',
      'two_sided': false,
      'custom_backside': false,
      'backside': 'back.png',
      'pdf_path': 'output',
      'image_type': 'png',
      'spacing': 0,
      'mode': 'default',
      'gamma_correction': true,
      'reference_points': true,
      'stagger': true,
      'x_axis_offset': 0.75,
      'user_agent': 'decklist_to_pdf/0.1',
      'accept': 'application/json;q=0.9,*/*;q=0.8',
      'worker_threads': 4,
      'dpi': 300,
      'bulk_json_path': '',
    });
    if (overrideConfig != null) {
      conf.addAll(overrideConfig);
    }
    if (File('decklist_to_pdf.conf').existsSync()) {
      //stderr.writeln('Loading configuration from decklist_to_pdf.conf');
      readConfig();
    }
    consts = generateConstants();
    consts['image_format'] = 'png';
  }

  void readConfig() {
    final file = File('decklist_to_pdf.conf');
    if (!file.existsSync()) return;
    final lines = file.readAsLinesSync();
    for (var line in lines) {
      line = line.trim();
      if (line.isEmpty || line.startsWith('#')) {
        continue; // skip comments and empty lines
      }
      final parts = line.split(':');
      if (parts[0].isEmpty || parts[1].isEmpty) {
        continue; // ignore malformed lines
      }
      final key = parts[0].trim();
      final value = parts.length > 1 ? parts.sublist(1).join(':').trim() : '';
      if (!conf.containsKey(key)) continue; // ignore unknown keys
      if (value == 'True' || value == 'true') {
        conf[key] = true;
      } else if (value == 'False' || value == 'false') {
        conf[key] = false;
      } else {
        final intVal = int.tryParse(value);
        if (intVal != null) {
          conf[key] = intVal;
          continue;
        }
        final doubleVal = double.tryParse(value);
        if (doubleVal != null) {
          conf[key] = doubleVal;
          continue;
        }
        conf[key] = value;
      }
    }
  }

  Future<void> initialize({bool fetchBulk = true, String? hivePath}) async {
    readConfig();
    // set a flag to let data service know to wate until json download is done

    if (fetchBulk) {
      await fetchBulkJson(ask: false);
    }
    await setupDatabase(hivePath: hivePath);
    // final bulkPath = conf['bulk_json_path'] as String;
    // cardData.addAll(loadCardDictionary(bulkPath));
  }

  Future<void> setupDatabase({String? hivePath}) async {
    List releaseSchedule = [];
    final finalHivePath = hivePath ?? p.join(Directory.current.path, 'hive_db');
    await CardDataService.initializeAndLoadData(
      conf['bulk_json_path'] as String,
      releaseSchedule,
      hivePath: finalHivePath,
    );
  }

  Future<String> fetchBulkJson({bool ask = true}) async {
    CardDataService.isScryfallDownloadComplete = false;
    try {
      final headers = <String, String>{
        'User-Agent': conf['user_agent'].toString(),
        'Accept': conf['accept'].toString(),
      };
      final meta = await http.get(
        Uri.parse('https://api.scryfall.com/bulk-data/default-cards'),
        headers: headers,
      );
      if (meta.statusCode != 200) {
        throw Exception('Failed to fetch bulk metadata');
      }
      final metaJson = jsonDecode(meta.body) as Map<String, dynamic>;
      final bulkUri = metaJson['download_uri'] as String;
      final basename = p.basename(bulkUri);
      final local = p.join('scryfall_bulk_json', basename);
      await Directory(p.dirname(local)).create(recursive: true);
      if (!File(local).existsSync()) {
        final resp = await http.get(Uri.parse(bulkUri), headers: headers);
        if (resp.statusCode != 200) {
          throw Exception('Failed to download bulk json');
        }
        File(local).writeAsBytesSync(resp.bodyBytes);
      }
      conf['bulk_json_path'] = local;
      return local;
    } finally {
      CardDataService.isScryfallDownloadComplete = true;
    }
  }

  Map<String, dynamic> loadCardDictionary(String filepath) {
    final file = File(filepath);

    final parsedPath = p.join(
      p.dirname(filepath),
      'parsed_${p.basename(filepath)}',
    );
    final parsedFile = File(parsedPath);
    if (parsedFile.existsSync()) {
      final data =
          jsonDecode(parsedFile.readAsStringSync()) as Map<String, dynamic>;
      return data;
    }
    if (!file.existsSync()) throw Exception('Bulk json not found: $filepath');
    final data = jsonDecode(file.readAsStringSync()) as List<dynamic>;
    final map = <String, dynamic>{};
    for (final card in data.cast<Map<String, dynamic>>()) {
      final setSym = (card['set'] ?? '').toString().toLowerCase();
      final collector = card['collector_number']?.toString() ?? '';
      final key = '$setSym-$collector';
      final layout = card['layout'];
      if (layout == 'transform' ||
          layout == 'modal_dfc' ||
          layout == 'double_faced_token' ||
          layout == 'reversible_card') {
        var side = 'A';
        if (card.containsKey('card_faces')) {
          for (final face
              in (card['card_faces'] as List<dynamic>)
                  .cast<Map<String, dynamic>>()) {
            map['${key}_$side'] = {
              'name': face['name'],
              'image_uris': face['image_uris'],
              'layout': layout,
              'two_sided': true,
              "other_face": "${key}_${side == 'A' ? 'B' : 'A'}",
              'border_color': card['border_color'],
            };
            side = 'B';
          }
          map[key] = {
            'name': card['name'],
            'set': card['set'],
            'collector_number': collector,
            'layout': layout,
            'two_sided': true,
            'faces': [map['${key}_A'], map['${key}_B']],
            'border_color': card['border_color'],
          };
        }
      } else if ([
        'normal',
        'token',
        'split',
        'layout',
        'flip',
        'mutate',
        'adventure',
        'emblem',
        'scheme',
        'vanguard',
        'planar',
        'phenomenon',
        'saga',
        'augment',
        'leveler',
        'prototype',
        'host',
        'case',
        'class',
        'meld',
      ].contains(layout)) {
        map[key] = {
          'name': card['name'],
          'set': card['set'],
          'collector_number': collector,
          'image_uris': card['image_uris'],
          'layout': layout,
          'two_sided': false,
          'border_color': card['border_color'],
        };
      } else if (layout != 'art_series') {
        stderr.writeln("Unknown layout $layout for card ${card['name']}");
      }
    }
    parsedFile.writeAsStringSync(jsonEncode(map));
    return map;
  }

  Map<String, dynamic> cardDataLookup(String decklistLine) {
    var line = decklistLine.trim();
    var forceSide = 0;
    if (line.startsWith('!!')) {
      forceSide = 2;
      line = line.substring(2).trim();
    } else if (line.startsWith('!')) {
      forceSide = 1;
      line = line.substring(1).trim();
    }
    final start = line.indexOf('(');
    final end = line.indexOf(')');
    if (start < 0 || end < 0) {
      throw Exception('Invalid decklist line: $decklistLine');
    }
    final setSymbol = line.substring(start + 1, end).toLowerCase();
    final parts = line.trim().split(RegExp(r'\s+'));
    final last = parts.last;
    final key = '$setSymbol-$last';
    dynamic data = {};
    try {
      data = CardDataService.getCardByKey(key) as Map<String, dynamic>;
    } catch (e) {
      throw Exception('Card not found for key $key in line: $decklistLine');
    }
    return {
      'name': line.substring(0, start - 1),
      'key': (forceSide == 0 ? key : '${key}_${forceSide == 1 ? 'A' : 'B'}'),
      'black_border': data['border_color'] == 'black',
      'force_side': forceSide,
      'sides': data['faces'],
      'image_uris': data.containsKey('image_uris')
          ? data['image_uris']
          : data['faces'][forceSide - 1]['image_uris'],
    };
  }

  void readDecklist(String filepath) {
    final file = File(filepath);
    if (!file.existsSync()) {
      throw Exception('Decklist file $filepath not found');
    }
    decklist.clear();
    final raw = file.readAsStringSync();
    final lines = raw.split('\n');
    for (var line in lines) {
      if (line.endsWith('\r')) line = line.substring(0, line.length - 1);
      if (line.isEmpty) continue;
      if (line.startsWith('#')) continue;
      final firstSpace = line.indexOf(' ');
      if (firstSpace < 0) {
        stderr.writeln('Skipping malformed decklist line (no space): "$line"');
        continue;
      }
      final copies = int.parse(line.substring(0, firstSpace).trim());
      var rest = line.substring(firstSpace + 1).trim();
      if (rest.contains('||')) {
        final faces = rest.split('||').map((f) {
          final t = f.trim();
          if (t.startsWith('*')) {
            final name = t.substring(1);
            return {
              'name': name,
              'key': name,
              'black_border': false,
              'custom': true,
            };
          } else {
            return cardDataLookup(t);
          }
        }).toList();
        for (var i = 0; i < copies; i++) {
          decklist.add({
            'sides': faces,
            'copies': 1,
            'two_sided': true,
            'composite': true,
          });
        }
        continue;
      }
      if (rest.startsWith('*')) {
        final name = rest.substring(1).trim();
        final entry = {
          'name': name,
          'key': name,
          'two_sided': false,
          'black_border': false,
          'custom': true,
          'composite': false,
          'copies': copies,
        };
        for (var i = 0; i < copies; i++) {
          decklist.add(entry);
        }
        continue;
      }
      final entry = cardDataLookup(rest);
      entry.addAll({
        'copies': copies,
        'composite': false,
        'two_sided': entry['sides'] != null,
        'custom': false,
      });
      for (var i = 0; i < copies; i++) {
        if (entry['sides'] != null && entry['sides'] is List) {
          decklist.add({
            'sides': entry['sides'],
            'copies': 1,
            'two_sided': true,
            'composite': false,
          });
        } else {
          decklist.add(entry);
        }
      }
    }
  }

  Map<String, dynamic> generateConstants() {
    final cardWidthMm = 63.0;
    final cardHeightMm = 88.0;
    final spacingMm = conf['spacing']?.toDouble() ?? 0.0;
    final dpi = conf['dpi'] as int;
    int mmToPx(double mm) => (mm * dpi / 25.4).round();

    final cardWidthPx = mmToPx(cardWidthMm);
    final cardHeightPx = mmToPx(cardHeightMm);
    final spacingPx = mmToPx(spacingMm);

    final pageWidthPx = mmToPx(210.0);
    final pageHeightPx = mmToPx(297.0);

    final gridWidthPx = 3 * cardWidthPx + 2 * spacingPx;
    final gridHeightPx = 3 * cardHeightPx + 2 * spacingPx;

    final xAxisOffsetPx = mmToPx((conf['x_axis_offset'] as num).toDouble());
    final gridXOffsetPx = ((pageWidthPx - gridWidthPx) / 2) + xAxisOffsetPx;
    final gridYOffsetPx = ((pageHeightPx - gridHeightPx) / 2);

    final cardPositionsPx = List.generate(3, (row) {
      return List.generate(3, (col) {
        final x = (gridXOffsetPx + col * (cardWidthPx + spacingPx)).round();
        final y =
            (pageHeightPx -
                    (gridYOffsetPx +
                        (3 - row) * cardHeightPx +
                        row * spacingPx))
                .round();
        return [x, y];
      });
    });

    final a4Pt = [210.0 * 72.0 / 25.4, 297.0 * 72.0 / 25.4];

    final bgBox = [0, 0, pageWidthPx, pageHeightPx];

    final markerRects = List.generate(4, (i) {
      final x = (i % 2) * (cardWidthPx + spacingPx);
      final y = (i ~/ 2) * (cardHeightPx + spacingPx);
      return [x, y, cardWidthPx, cardHeightPx];
    });

    return {
      'deck_size': 0,
      'total_pages': 0,
      'card_width_px': cardWidthPx,
      'card_height_px': cardHeightPx,
      'page_width_px': pageWidthPx,
      'page_height_px': pageHeightPx,
      'card_positions_px': cardPositionsPx,
      'A4': a4Pt,
      'bg_box': bgBox,
      'marker_rects': markerRects,
    };
  }

  // network fetch with simple caching
  void fetchImageForCard(
    Map<String, dynamic> card, {
    bool preview = false,
  }) async {
    final key = card['key'] as String;
    if (imageCache.containsKey(key)) {
      return;
    }
    if (card['faces'] != null && card['faces'] is List) {
      // two sided card
      for (final side in (card['faces'] as List).cast<Map<String, dynamic>>()) {
        fetchImageForCard(side, preview: preview);
      }
      return;
    }
    final imageUrisMap = card['image_uris'] as Map<String, dynamic>?;
    if (imageUrisMap == null) {
      stderr.writeln('No image_uris found for key $key');
      return;
    }
    final destination = p.join(
      'image_cache',
      conf['image_type'] as String,
      preview ? 'jpg' : 'png',
      '$key.${consts['image_format'] ?? 'png'}',
    );
    try {
      await fetchImage(
        imageUrisMap[conf['image_type']] as String,
        destination,
        key,
        card['custom'] == true,
        preview,
      );
    } catch (e) {
      stderr.writeln('Failed to fetch image for key $key: $e');
    }
  }

  Future<void> fetchImage(
    String imageUrl,
    String destination,
    String key,
    bool custom,
    bool preview,
  ) async {
    // If imageUrl looks like local (custom), just open from disk
    if (custom) {
      final file = File(imageUrl);
      if (!file.existsSync()) {
        throw Exception('Custom image not found: $imageUrl');
      }
      final bytes = file.readAsBytesSync();
      final image = img.decodeImage(bytes);
      if (image == null) throw Exception('Failed to decode $imageUrl');
      imageCache[key] = image;
      return;
    }

    // network fetch with simple caching

    final destFile = File('$destination${preview ? '_preview' : ''}');
    await Directory(p.dirname(destination)).create(recursive: true);
    if (!destFile.existsSync()) {
      final res = await http.get(
        Uri.parse(imageUrl),
        headers: {'User-Agent': conf['user_agent'], 'Accept': conf['accept']},
      );
      if (res.statusCode == 200) {
        destFile.writeAsBytesSync(res.bodyBytes);
      } else {
        throw Exception('Failed to download $imageUrl');
      }
    }
    final bytes = destFile.readAsBytesSync();
    var image = img.decodeImage(bytes);
    if (image == null) throw Exception('Failed to decode $destination');
    // resize to card size in pixels
    final resized = img.copyResize(
      image,
      width: consts['card_width_px'],
      height: consts['card_height_px'],
      interpolation: img.Interpolation.average,
    );
    // Apply gamma correction if enabled
    if (conf['gamma_correction'] == true) {
      imageCache[key] = applyGammaCorrection(resized);
    } else {
      imageCache[key] = resized;
    }
  }

  img.Image applyGammaCorrection(img.Image image, {double gamma = 2.2}) {
    final corrected = img.Image.from(image);
    for (int y = 0; y < corrected.height; y++) {
      for (int x = 0; x < corrected.width; x++) {
        final c = corrected.getPixel(x, y);
        final colorInt = c as int;
        final r = getRed(colorInt);
        final g = getGreen(colorInt);
        final b = getBlue(colorInt);
        final a = getAlpha(colorInt);
        int correct(int v) =>
            (255 * math.pow(v / 255, 1 / gamma)).clamp(0, 255).toInt();
        corrected.setPixelRgba(x, y, correct(r), correct(g), correct(b), a);
      }
    }
    return corrected;
  }

  Future<void> createImageCache() async {
    final imageType = conf['image_type'] as String;
    // create a dedicated png folder under image_cache/<imageType>/png to match Python behaviour
    final cacheDir = Directory('image_cache/$imageType/png');
    await cacheDir.create(recursive: true);

    // collect unique keys to avoid duplicate downloads
    final keysToFetch = <String, Map<String, dynamic>>{};
    for (final item in decklist) {
      if (item.containsKey('sides') && item['sides'] != null) {
        for (final side
            in (item['sides'] as List).cast<Map<String, dynamic>>()) {
          if (side['key'] == 'back' || side['custom'] == true) continue;
          final k = side['key'] as String;
          keysToFetch.putIfAbsent(k, () => side);
        }
      } else if (item.containsKey('key')) {
        final k = item['key'] as String;
        if (k != 'back' && !(item['custom'] == true)) {
          keysToFetch.putIfAbsent(k, () => item);
        }
      }
    }

    final tryOrder = [
      'png',
      'large',
      'normal',
      'small',
      'art_crop',
      'border_crop',
    ];

    // prepare entries queue for safe synchronous pop by workers
    final entriesQueue = Queue<MapEntry<String, Map<String, dynamic>>>.from(
      keysToFetch.entries,
    );

    var workerThreads = 4;
    try {
      final wt = conf['worker_threads'];
      if (wt is int && wt > 0) workerThreads = wt;
    } catch (e) {
      // fallback to default
    }

    // worker function: each worker takes the next index and processes it
    Future<void> worker() async {
      while (true) {
        // removeFirst() is synchronous; since we don't await here, it's safe in
        // the single-isolate event loop and avoids index arithmetic races.
        if (entriesQueue.isEmpty) break;
        final entry = entriesQueue.removeFirst();
        final key = entry.key;
        final side = entry.value;

        final destination = p.join(
          'image_cache',
          imageType,
          'png',
          '$key.${consts['image_format'] ?? 'png'}',
        );

        // if already exists on disk, load into memory via fetchImage
        try {
          if (File(destination).existsSync()) {
            stderr.writeln('Image already cached for $key -> $destination');
            await fetchImage(destination, destination, key, false, false);
            continue;
          }
        } catch (e) {
          // ignore and attempt download
        }

        if (side['custom'] == true) {
          final local = 'custom_cards/${side['name']}.png';
          try {
            await fetchImage(local, local, key, true, false);
          } catch (e) {
            stderr.writeln('Failed to load custom image for $key: $e');
          }
          continue;
        }

        final imageUrisMap = side['image_uris'] as Map<String, dynamic>?;
        if (imageUrisMap == null) {
          stderr.writeln('No image_uris found for key $key');
          continue;
        }

        var downloaded = false;
        for (final t in tryOrder) {
          final uri = imageUrisMap.containsKey(t)
              ? (imageUrisMap[t] as String)
              : null;
          if (uri == null || uri.isEmpty) continue;
          try {
            stderr.writeln('Trying $t image for key $key -> $uri');
            await fetchImage(uri, destination, key, false, false);
            downloaded = true;
            break;
          } catch (e) {
            stderr.writeln('Download failed for $key with type $t: $e');
          }
        }
        if (!downloaded) {
          stderr.writeln(
            'Warning: Could not download any image for $key; will use placeholder',
          );
        }
      }
    }

    final workers = List<Future<void>>.generate(workerThreads, (_) => worker());
    await Future.wait(workers);
  }

  Future<Uint8List> renderPages({
    String? decklistName,
    bool? twoSided,
    bool? stagger,
  }) async {
    await createImageCache();
    final cardsPerPage = 9;
    final totalPages = ((decklist.length + cardsPerPage - 1) / cardsPerPage)
        .floor();
    final outPdf = pw.Document();
    final isTwoSided = twoSided ?? (conf['two_sided'] == true);
    final isStagger = stagger ?? (conf['stagger'] == true);
    final showReferencePoints = conf['reference_points'] == true;
    // Pattern logic for page order
    List<List<int>> pattern = [];
    if (isTwoSided && isStagger) {
      pattern = [
        [0, 0],
        [1, 0],
        [0, 1],
        [1, 1],
      ];
    } else if (isTwoSided && !isStagger) {
      pattern = [
        [0, 0],
        [0, 1],
        [1, 0],
        [1, 1],
      ];
    } else {
      pattern = [
        [0, 0],
        [1, 0],
      ];
    }
    // Store rendered pages by (page,side)
    final Map<String, Uint8List> pages = {};
    // Reference points and background box
    final bgBox = consts['bg_box'] as List?;
    final markerRects = consts['marker_rects'] as List?;
    for (var pIndex = 0; pIndex < totalPages; pIndex++) {
      for (var side = 0; side < (isTwoSided ? 2 : 1); side++) {
        final pageImg = img.Image(
          width: consts['page_width_px'] as int,
          height: consts['page_height_px'] as int,
        );
        // Fill white background
        img.fill(pageImg, color: img.ColorUint8(getColor(255, 255, 255, 255)));
        // Draw black background box
        if (bgBox != null && bgBox.length == 4) {
          img.fillRect(
            pageImg,
            x1: bgBox[0].round(),
            y1: bgBox[1].round(),
            x2: bgBox[2].round(),
            y2: bgBox[3].round(),
            color: img.ColorUint8(getColor(0, 0, 0, 255)),
          );
        }
        // Draw reference points
        if (showReferencePoints && markerRects != null) {
          for (final rect in markerRects) {
            if (rect is List && rect.length == 4) {
              img.fillRect(
                pageImg,
                x1: rect[0].round(),
                y1: rect[1].round(),
                x2: rect[2].round(),
                y2: rect[3].round(),
                color: img.ColorUint8(getColor(0, 0, 0, 255)),
              );
            }
          }
        }
        var cardIndex = pIndex * cardsPerPage;
        for (var row = 0; row < 3; row++) {
          for (var col = 0; col < 3; col++) {
            if (cardIndex >= decklist.length) break;
            final card = decklist[cardIndex];
            String key = '';
            if (card['sides'] != null && card['sides'] is List) {
              final sides = card['sides'] as List;
              if (sides.length > side) {
                key = sides[side]['key'] as String;
              } else {
                key = sides[0]['key'] as String;
              }
            } else {
              key = card['key'] as String;
            }
            var im = imageCache[key];
            if (im == null) {
              final pw = consts['card_width_px'] as int;
              final ph = consts['card_height_px'] as int;
              final placeholder = img.Image(width: pw, height: ph);
              img.fill(
                placeholder,
                color: img.ColorUint8(getColor(255, 255, 255, 255)),
              );
              imageCache[key] = placeholder;
              im = placeholder;
            }
            final x = consts['card_positions_px'][row][col][0] as int;
            final y = consts['card_positions_px'][row][col][1] as int;
            for (var yy = 0; yy < im.height; yy++) {
              for (var xx = 0; xx < im.width; xx++) {
                final px = im.getPixel(xx, yy);
                pageImg.setPixel(x + xx, y + yy, px);
              }
            }
            cardIndex++;
          }
        }
        final pngBytes = img.encodePng(pageImg);
        pages['$pIndex,$side'] = pngBytes;
      }
    }
    // Merge pages in pattern order
    for (var i = 0; i < totalPages; i += 2) {
      for (final set in pattern) {
        final key = '${i + set[0]},${set[1]}';
        if ((i + set[0]) >= totalPages) continue;
        final pageBytes = pages[key];
        if (pageBytes == null) continue;
        final pwImage = pw.MemoryImage(pageBytes);
        outPdf.addPage(
          pw.Page(
            build: (context) => pw.Center(child: pw.Image(pwImage)),
            pageFormat: pdf.PdfPageFormat(
              consts['A4'][0] as double,
              consts['A4'][1] as double,
            ),
          ),
        );
      }
    }
    return outPdf.save();
  }

  void writeConfig() {
    final file = File('decklist_to_pdf.conf');
    final sink = file.openWrite(mode: FileMode.write);
    for (final config in conf.keys) {
      switch (config) {
        case 'bulk_json_path':
          sink.writeln('# relative path to scryfall bulk json file');
          sink.writeln('bulk_json_path:${conf['bulk_json_path']}');
          break;
        case 'decklist_path':
          sink.writeln(
            '# relative path to decklist listing unique cards one per line in of the formats:',
          );
          sink.writeln('# copies name (SET) collector_number');
          sink.writeln(
            '# copies name (SET) collector_number | backside.jpg/*.png',
          );
          sink.writeln(
            '# copies name (SET) collector_number | (SET) collector_number',
          );
          sink.writeln('decklist_path:${conf['decklist_path']}');
          break;
        case 'two_sided':
          sink.writeln('# two sided printing');
          sink.writeln('two_sided:${conf['two_sided']}');
          break;
        case 'custom_backside':
          sink.writeln('# use custom backside');
          sink.writeln('custom_backside:${conf['custom_backside']}');
          break;
        case 'backside':
          sink.writeln('# default backside image');
          sink.writeln('backside:${conf['backside']}');
          break;
        case 'pdf_path':
          sink.writeln('# output pdf path (without .pdf extension)');
          sink.writeln('pdf_path:${conf['pdf_path']}');
          break;
        case 'image_type':
          sink.writeln('# image type to use from scryfall (png/jpg/webp)');
          sink.writeln('image_type:${conf['image_type']}');
          break;
        case 'spacing':
          sink.writeln('# spacing between cards in mm');
          sink.writeln('spacing:${conf['spacing']}');
          break;
        case 'mode':
          sink.writeln('# rendering mode (default/compact)');
          sink.writeln('mode:${conf['mode']}');
          break;
        case 'gamma_correction':
          sink.writeln('# apply gamma correction to images');
          sink.writeln('gamma_correction:${conf['gamma_correction']}');
          break;
        case 'reference_points':
          sink.writeln('# show reference points for cutting');
          sink.writeln('reference_points:${conf['reference_points']}');
          break;
        case 'stagger':
          sink.writeln('# stagger two sided pages');
          sink.writeln('stagger:${conf['stagger']}');
          break;
        case 'x_axis_offset':
          sink.writeln('# x axis offset in mm');
          sink.writeln('x_axis_offset:${conf['x_axis_offset']}');
          break;
        case 'user_agent':
          sink.writeln('# user agent for scryfall requests');
          sink.writeln('user_agent:${conf['user_agent']}');
          break;
        case 'accept':
          sink.writeln('# accept header for scryfall requests');
          sink.writeln('accept:${conf['accept']}');
          break;
        case 'worker_threads':
          sink.writeln('# number of worker threads for image downloading');
          sink.writeln('worker_threads:${conf['worker_threads']}');
          break;
        case 'dpi':
          sink.writeln('# output dpi (300 recommended)');
          sink.writeln('dpi:${conf['dpi']}');
          break;
        default:
          break;
      }
    }
    sink.close();
  }

  void updateConfigIfMissing() {
    final confUpdateCheck = Map<String, dynamic>.from(conf);
    confUpdateCheck.remove('bulk_json_path');
    for (final a in confUpdateCheck.keys) {
      confUpdateCheck[a] = false;
    }
    try {
      final file = File('decklist_to_pdf.conf');
      if (!file.existsSync()) return;
      final lines = file.readAsLinesSync();
      for (final line in lines) {
        final l = line.trim();
        if (l.isEmpty || l.startsWith('#')) continue;
        final parts = l.split(':');
        if (parts.isEmpty) continue;
        final key = parts[0].trim();
        if (confUpdateCheck.containsKey(key)) confUpdateCheck[key] = true;
      }
    } catch (e) {
      stderr.writeln('decklist_to_pdf.conf inaccessible.');
      throw Exception('decklist_to_pdf.conf inaccessible.');
    }
    final missingConfigs = confUpdateCheck.entries
        .where((e) => e.value == false)
        .map((e) => e.key)
        .toList();
    if (missingConfigs.isNotEmpty) {
      stderr.writeln(
        'Writing missing configuration entries: ${missingConfigs.join(', ')}',
      );
      writeConfig();
    }
  }

  // Deck manager functions go here
  void addTagToCard(String cardKey, String tagId) {}
  // Implementation for adding a tag to a card
}
