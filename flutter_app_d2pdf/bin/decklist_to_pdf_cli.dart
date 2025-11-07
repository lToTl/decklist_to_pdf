// CLI entrypoint for decklist_to_pdf
// This file contains the main() function and argument parsing logic.

import 'dart:io';
import 'package:path/path.dart' as p;
import 'package:flutter_app_d2pdf/decklist_to_pdf.dart';

Future<void> main(List<String> args) async {
  stderr.writeln('Starting decklist_to_pdf in Dart');
  // Instantiate core components
  var core = DecklistToPdfCore();
  // Ensure scryfall directory exists and fetch bulk json
  await core.fetchBulkJson(ask: false);
  final bulkPath = core.conf['bulk_json_path'] as String;
  core.cardData.addAll(core.loadCardDictionary(bulkPath));

  // Add image format
  core.consts['image_format'] = 'png';

  // Read arguments
  var i = 0;
  var range = args.length;
  while (i < range) {
    var arg = args[i].trim();
    i += 1;
    if (arg.startsWith('--input') || arg.startsWith('-i')) {
      final val = args[i].trim();
      if (val.isNotEmpty) core.conf['decklist_path'] = 'input/$val.txt';
    } else if (arg.startsWith('--output') || arg.startsWith('-o')) {
      final val = args[i].trim();
      if (val.isNotEmpty) core.conf['pdf_path'] = 'output/$val.pdf';
    } else if (arg.startsWith('--two-sided') || arg.startsWith('-t')) {
      final val = args[i].trim().toLowerCase();
      if (val == 'true' || val == 'false') {
        core.conf['two_sided'] = val == 'true';
      }
    } else if (arg.startsWith('--custom-backside=') || arg.startsWith('-c=')) {
      final val = args[i].trim().toLowerCase();
      if (val == 'true' || val == 'false') {
        core.conf['custom_backside'] = val == 'true';
      }
    } else if (arg.startsWith('--backside=') || arg.startsWith('-b=')) {
      final val = args[i].trim();
      if (val.isNotEmpty) core.conf['backside'] = val;
    } else if (arg.startsWith('--image-type=') || arg.startsWith('-f=')) {
      final val = args[i].trim();
      if (val.isNotEmpty) core.conf['image_type'] = val;
    } else if (arg.startsWith('--spacing=') || arg.startsWith('-p=')) {
      final val = args[i].trim();
      final d = double.tryParse(val);
      if (d != null) core.conf['spacing'] = d;
    } else if (arg.startsWith('--mode=') || arg.startsWith('-m=')) {
      final val = args[i].trim();
      if (val.isNotEmpty) core.conf['mode'] = val;
    } else if (arg.startsWith('--gamma-correction=') || arg.startsWith('-g=')) {
      final val = args[i].trim().toLowerCase();
      if (val == 'true' || val == 'false') {
        core.conf['gamma_correction'] = val == 'true';
      }
    } else if (arg.startsWith('--reference-points=') || arg.startsWith('-r=')) {
      final val = args[i].trim().toLowerCase();
      if (val == 'true' || val == 'false') {
        core.conf['reference_points'] = val == 'true';
      }
    } else if (arg.startsWith('--stagger=') || arg.startsWith('-s=')) {
      final val = args[i].trim().toLowerCase();
      if (val == 'true' || val == 'false') core.conf['stagger'] = val == 'true';
    } else if (arg.startsWith('--x-axis-offset=') || arg.startsWith('-x=')) {
      final val = args[i].trim();
      final d = double.tryParse(val);
      if (d != null) core.conf['x_axis_offset'] = d;
    } else if (arg.startsWith('--dpi=') || arg.startsWith('-d=')) {
      final val = args[i].trim();
      final input = int.tryParse(val);
      if (input != null && i > 0) core.conf['dpi'] = input;
    } else if (arg.startsWith('--worker-threads=') || arg.startsWith('-w=')) {
      final val = args[i].trim();
      final input = int.tryParse(val);
      if (input != null && i > 0) core.conf['worker_threads'] = input;
    } else if (args.contains('--help') || args.contains('-h')) {
      stderr.writeln(
        '''Usage: dart decklist_to_pdf_cli.dart [--argument value]\narguments:\n  --help, -h          Show this help message\n  --input, -i       Name of the decklist file (without .txt) in input/\n                      Default is core.decklist.txt or input/core.decklist.txt\n  --output, -o  [string]        Output PDF file name (without .pdf)\n                    Default is output/<decklistname>.pdf\n  --two-sided, -t [true/false]   Enable two-sided printing (default: from ini)\n  --custom-backside, -c [true/false] Use custom backside image (default: from ini)\n  --backside, -b [string]   Custom backside image file (default: back.png)\n  --image-type, -f [string] Image type to fetch from scryfall\n  --spacing, -p [float]   Spacing between cards in mm (default: from ini)\n  --mode, -m [default/compact]   Layout mode (default: from ini)\n  --gamma-correction, -g [true/false] Enable gamma correction (default: from ini)\n  --reference-points, -r [true/false] Show reference points (\n  --stagger, -s [true/false]     Enable staggering for two-sided (default: from ini)\n  --x-axis-offset, -x [float]  Horizontal offset in mm (default: from ini)\n  --dpi, -d [int]        Dots per inch for image resizing (default: from ini)\n  --worker-threads, -w [int]   Number of parallel image download threads (default: from ini)\n  --user-agent,  -u [string]    User-Agent header for HTTP requests (default: from ini)\n  --accept, -a [string]        Accept header for HTTP requests (default: from ini)\n  --bulk-json-path, -j [string]  Path to scryfall bulk json file (default: fetched automatically)\n''',
      );
      return;
    }
    // Prompt for decklist name
    String decklistName = '';
    if (args.isNotEmpty && args[0].trim().isNotEmpty) {
      decklistName = args[0].trim();
    } else {
      stdout.write(
        'Enter decklist name (default: \\${core.conf['decklist_path']}): ',
      );
      final userInput = stdin.readLineSync()?.trim() ?? '';
      decklistName = userInput.isNotEmpty
          ? userInput
          : core.conf['decklist_path']
                .toString()
                .replaceAll('.txt', '')
                .replaceAll('input/', '');
    }
    if (decklistName.isNotEmpty && decklistName != core.conf['decklist_path']) {
      core.conf['decklist_path'] = 'input/\\$decklistName.txt';
      core.writeConfig();
    }
    final deckPath = p.join('input', '$decklistName.txt');
    if (File(deckPath).existsSync()) {
      core.readDecklist(deckPath);
    } else if (File(core.conf['decklist_path']).existsSync()) {
      core.readDecklist(core.conf['decklist_path']);
    } else if (File('core.decklist.txt').existsSync()) {
      core.readDecklist('core.decklist.txt');
    } else {
      stderr.writeln(
        'No decklist found. Put a decklist file at input/<name>.txt or core.decklist.txt',
      );
      return;
    }

    core.consts['deck_size'] = core.decklist.length;
    core.consts['total_pages'] = ((core.decklist.length + 8) / 9).floor();

    final pdfBytes = await core.renderPages(decklistName: decklistName);
    final outDir = Directory('output');
    await outDir.create(recursive: true);
    final outFile = File(p.join(outDir.path, '$decklistName.pdf'));
    await outFile.writeAsBytes(pdfBytes);
    stderr.writeln('PDF created at output/$decklistName.pdf');
  }
}
