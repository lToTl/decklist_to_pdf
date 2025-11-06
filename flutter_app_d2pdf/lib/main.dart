import 'dart:async';
import 'dart:io';
//import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:file_picker/file_picker.dart';
import 'package:super_clipboard/super_clipboard.dart';
import 'package:image/image.dart' as img;

import 'decklist_to_pdf.dart';
import 'package:path_provider/path_provider.dart';

void main() {
  SystemChrome.setSystemUIOverlayStyle(
    SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      statusBarBrightness: Brightness.light,
      systemNavigationBarColor: Colors.white,
      systemNavigationBarIconBrightness: Brightness.dark,
      systemNavigationBarDividerColor: Colors.grey,
    ),
  );
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => MyAppState(),
      child: MaterialApp(
        title: 'CardMonger',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.cyan),
        ),
        home: const PageFolder(key: Key('PageFolder')),
      ),
    );
  }
}

class MyAppState extends ChangeNotifier {
  var core = DecklistToPdfCore();

  void clearDeck() {
    core.readDecklist(core.conf['decklist_path']!);
    notifyListeners();
  }

  void setDeck(String path) {
    core.readDecklist(path);
    notifyListeners();
  }

  void addCopy(int index) {
    if (index < 0 || index >= core.decklist.length) return;
    core.decklist.insert(index, Map.from(core.decklist[index]));
    notifyListeners();
  }

  void addCard(Map<String, dynamic> item, int index) {
    core.decklist.insert(index, item);
    core.fetchGUIImage(item['id'] as String, item['custom']);
    notifyListeners();
  }

  void removeCard(int index) {
    core.decklist.removeAt(index);
    notifyListeners();
  }

  void moveCard(int oldIndex, int newIndex) {
    if (oldIndex < newIndex) {
      newIndex -= 1;
    }
    final item = core.decklist.removeAt(oldIndex);
    core.decklist.insert(newIndex, item);
    notifyListeners();
  }

  void updateConfig(String key, dynamic value) {
    core.conf[key] = value;
    core.writeConfig();
    //notifyListeners();
  }
}

class PageFolder extends StatefulWidget {
  const PageFolder({super.key});
  static const List<Tab> myTabs = <Tab>[
    Tab(text: 'DECKBUILDER', icon: Icon(Icons.build), key: Key('DeckBuilder')),
    Tab(
      text: 'PRINTINGPAGE',
      icon: Icon(Icons.print),
      key: Key('PrintingPage'),
    ),
  ];

  @override
  State<PageFolder> createState() => _PageFolderState();
}

class _PageFolderState extends State<PageFolder> {
  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: PageFolder.myTabs.length,
      child: SafeArea(
        child: Scaffold(
          appBar: AppBar(flexibleSpace: const TabBar(tabs: PageFolder.myTabs)),
          body: TabBarView(
            children: PageFolder.myTabs.map((Tab tab) {
              final String label = tab.text!.toLowerCase();
              return label == 'deckbuilder'
                  ? const DeckBuilder()
                  : const PrintingPage();
            }).toList(),
          ),
        ),
      ),
    );
  }
}

class DeckBuilder extends StatefulWidget {
  const DeckBuilder({super.key});

  @override
  State<DeckBuilder> createState() => _DeckBuilderState();
}

class _DeckBuilderState extends State<DeckBuilder> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(flexibleSpace: const Text('Deck Builder')),
      body: const Center(child: Text('Deck Builder Screen')),
    );
  }
}

class PrintingPage extends StatefulWidget {
  const PrintingPage({super.key});

  @override
  State<PrintingPage> createState() => _PrintingPageState();
}

class _PrintingPageState extends State<PrintingPage> {
  bool _showOptions = false;

  void _toggleOptions() {
    setState(() {
      if (_showOptions == false) {
        _showOptions = true;
      } else {
        _showOptions = false;
      }
    });
  }

  Future<num?> _showNumberInputDialog(
    BuildContext context,
    String title,
    num initialValue, {
    bool isInteger = false,
  }) {
    final controller = TextEditingController(text: initialValue.toString());
    return showDialog<num>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(title),
          content: TextField(
            controller: controller,
            keyboardType: TextInputType.numberWithOptions(
              decimal: !isInteger,
              signed: false,
            ),
            autofocus: true,
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () {
                final value = isInteger
                    ? int.tryParse(controller.text)
                    : double.tryParse(controller.text);
                if (value != null) {
                  Navigator.of(context).pop(value);
                }
              },
              child: const Text('OK'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Printing'),
        actions: [
          IconButton(
            key: const Key('PrintingOptionsToggle'),
            icon: const Icon(Icons.build),
            tooltip: 'Options',
            onPressed: _toggleOptions,
          ),
        ],
      ),
      body: Row(
        children: [
          // Main printing content
          Expanded(
            child: PagePreview(
              key: const Key('Printing options menu'),
              core: Provider.of<MyAppState>(context).core,
            ),
          ),

          // Hidable options sidebar (printing-related settings)
          AnimatedContainer(
            duration: const Duration(milliseconds: 250),
            width: _showOptions ? 320.0 : 0.0,
            curve: Curves.easeInOut,
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: SizedBox(
                width: 320.0,
                child: _showOptions
                    ? Material(
                        elevation: 4,
                        child: Container(
                          width: 320,
                          color: Theme.of(context).canvasColor,
                          child: Column(
                            children: [
                              Padding(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 12.0,
                                  vertical: 12.0,
                                ),
                                child: Row(
                                  mainAxisAlignment:
                                      MainAxisAlignment.spaceBetween,
                                  children: [
                                    Row(
                                      children: const [
                                        Icon(Icons.build),
                                        SizedBox(width: 8),
                                        Text(
                                          'Options',
                                          style: TextStyle(
                                            fontSize: 18,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                      ],
                                    ),
                                    IconButton(
                                      icon: const Icon(Icons.close),
                                      onPressed: _toggleOptions,
                                    ),
                                  ],
                                ),
                              ),
                              const Divider(height: 1),
                              // Decklist_to_pdf-specific option entries
                              Expanded(
                                child: Consumer<MyAppState>(
                                  builder: (context, appState, child) {
                                    return ListView(
                                      padding: const EdgeInsets.all(8.0),
                                      children: [
                                        SwitchListTile(
                                          title: const Text(
                                            'Two-sided printing',
                                          ),
                                          value:
                                              appState.core.conf['two_sided']
                                                  as bool,
                                          onChanged: (v) {
                                            appState.updateConfig(
                                              'two_sided',
                                              v,
                                            );
                                          },
                                        ),
                                        SwitchListTile(
                                          title: const Text(
                                            'Stagger page order',
                                          ),
                                          value:
                                              appState.core.conf['stagger']
                                                  as bool,
                                          onChanged: (v) {
                                            appState.updateConfig('stagger', v);
                                          },
                                        ),
                                        SwitchListTile(
                                          title: const Text('Custom backside'),
                                          value:
                                              appState
                                                      .core
                                                      .conf['custom_backside']
                                                  as bool,
                                          onChanged: (v) {
                                            appState.updateConfig(
                                              'custom_backside',
                                              v,
                                            );
                                          },
                                        ),
                                        SwitchListTile(
                                          title: const Text('Gamma correction'),
                                          value:
                                              appState
                                                      .core
                                                      .conf['gamma_correction']
                                                  as bool,
                                          onChanged: (v) {
                                            appState.updateConfig(
                                              'gamma_correction',
                                              v,
                                            );
                                          },
                                        ),
                                        SwitchListTile(
                                          title: const Text('Reference points'),
                                          value:
                                              appState
                                                      .core
                                                      .conf['reference_points']
                                                  as bool,
                                          onChanged: (v) {
                                            appState.updateConfig(
                                              'reference_points',
                                              v,
                                            );
                                          },
                                        ),
                                        ListTile(
                                          title: const Text('Image Type'),
                                          trailing: DropdownButton<String>(
                                            value: appState
                                                .core
                                                .conf['image_type']
                                                .toString(),
                                            items:
                                                [
                                                  'png',
                                                  'large',
                                                  'normal',
                                                  'small',
                                                  'art_crop',
                                                  'border_crop',
                                                ].map((String value) {
                                                  return DropdownMenuItem<
                                                    String
                                                  >(
                                                    value: value,
                                                    child: Text(value),
                                                  );
                                                }).toList(),
                                            onChanged: (newValue) {
                                              if (newValue != null) {
                                                appState.updateConfig(
                                                  'image_type',
                                                  newValue,
                                                );
                                              }
                                            },
                                          ),
                                        ),
                                        ListTile(
                                          title: const Text('Mode'),
                                          trailing: DropdownButton<String>(
                                            value: appState.core.conf['mode']
                                                .toString(),
                                            items: ['default', 'bleed edge']
                                                .map((String value) {
                                                  return DropdownMenuItem<
                                                    String
                                                  >(
                                                    value: value,
                                                    child: Text(value),
                                                  );
                                                })
                                                .toList(),
                                            onChanged: (newValue) {
                                              if (newValue != null) {
                                                appState.updateConfig(
                                                  'mode',
                                                  newValue,
                                                );
                                              }
                                            },
                                          ),
                                        ),
                                        ListTile(
                                          title: const Text('Spacing (mm)'),
                                          subtitle: Text(
                                            appState.core.conf['spacing']
                                                .toString(),
                                          ),
                                          onTap: () async {
                                            final newValue =
                                                await _showNumberInputDialog(
                                                  context,
                                                  'Spacing (mm)',
                                                  appState.core.conf['spacing'],
                                                );
                                            if (newValue != null) {
                                              appState.updateConfig(
                                                'spacing',
                                                newValue,
                                              );
                                            }
                                          },
                                        ),
                                        ListTile(
                                          title: const Text(
                                            'X-axis offset (mm)',
                                          ),
                                          subtitle: Text(
                                            appState.core.conf['x_axis_offset']
                                                .toString(),
                                          ),
                                          onTap: () async {
                                            final newValue =
                                                await _showNumberInputDialog(
                                                  context,
                                                  'X-axis offset (mm)',
                                                  appState
                                                      .core
                                                      .conf['x_axis_offset'],
                                                );
                                            if (newValue != null) {
                                              appState.updateConfig(
                                                'x_axis_offset',
                                                newValue,
                                              );
                                            }
                                          },
                                        ),
                                        ListTile(
                                          title: const Text('Worker Threads'),
                                          subtitle: Text(
                                            appState.core.conf['worker_threads']
                                                .toString(),
                                          ),
                                          onTap: () async {
                                            final newValue =
                                                await _showNumberInputDialog(
                                                  context,
                                                  'Worker Threads',
                                                  appState
                                                      .core
                                                      .conf['worker_threads'],
                                                  isInteger: true,
                                                );
                                            if (newValue != null) {
                                              appState.updateConfig(
                                                'worker_threads',
                                                newValue,
                                              );
                                            }
                                          },
                                        ),
                                        ListTile(
                                          title: const Text('DPI'),
                                          subtitle: Text(
                                            appState.core.conf['dpi']
                                                .toString(),
                                          ),
                                          onTap: () async {
                                            final newValue =
                                                await _showNumberInputDialog(
                                                  context,
                                                  'DPI',
                                                  appState.core.conf['dpi'],
                                                  isInteger: true,
                                                );
                                            if (newValue != null) {
                                              appState.updateConfig(
                                                'dpi',
                                                newValue,
                                              );
                                            }
                                          },
                                        ),
                                        ListTile(
                                          leading: const Icon(Icons.folder),
                                          title: const Text('Output PDF path'),
                                          subtitle: Text(
                                            appState.core.conf['pdf_path']
                                                as String,
                                          ),
                                          onTap: () async {
                                            String?
                                            outputFile = await FilePicker
                                                .platform
                                                .saveFile(
                                                  dialogTitle:
                                                      'Please select an output file:',
                                                  fileName: 'output.pdf',
                                                );

                                            if (outputFile != null) {
                                              appState.updateConfig(
                                                'pdf_path',
                                                outputFile,
                                              );
                                            }
                                          },
                                        ),
                                        ListTile(
                                          leading: const Icon(Icons.image),
                                          title: const Text('Backside image'),
                                          subtitle: Text(
                                            appState.core.conf['backside']
                                                as String,
                                          ),
                                          trailing: Row(
                                            mainAxisSize: MainAxisSize.min,
                                            children: [
                                              IconButton(
                                                icon: const Icon(
                                                  Icons.content_paste,
                                                ),
                                                tooltip: 'Paste from clipboard',
                                                onPressed: () async {
                                                  final reader =
                                                      await SystemClipboard
                                                          .instance
                                                          ?.read();
                                                  if (reader == null ||
                                                      !reader.canProvide(
                                                        Formats.png,
                                                      )) {
                                                    if (!context.mounted) {
                                                      return;
                                                    }
                                                    ScaffoldMessenger.of(
                                                      context,
                                                    ).showSnackBar(
                                                      const SnackBar(
                                                        content: Text(
                                                          'No image in clipboard.',
                                                        ),
                                                      ),
                                                    );
                                                    return;
                                                  }

                                                  dynamic raw = reader.getFile(
                                                    Formats.png,
                                                    (size) =>
                                                        const Stream.empty(),
                                                  );

                                                  // getFile may return a Future or a record like
                                                  // (Future<Object?>, ReadProgress). Normalize it.
                                                  try {
                                                    if (raw is Future) {
                                                      raw = await raw;
                                                    }
                                                  } catch (e) {
                                                    return;
                                                  }

                                                  dynamic dataObj;
                                                  // Try to extract positional fields from a record
                                                  try {
                                                    final df =
                                                        raw.$1; // may throw
                                                    // If we got here, raw is a record
                                                    final dataFuture =
                                                        df as Future<dynamic>;
                                                    dataObj = await dataFuture;
                                                  } catch (e) {
                                                    // Not a record; raw might be the data or a Future
                                                    if (raw is Future) {
                                                      try {
                                                        dataObj = await raw;
                                                      } catch (e) {
                                                        return;
                                                      }
                                                    } else {
                                                      dataObj = raw;
                                                    }
                                                  }

                                                  if (dataObj == null) return;

                                                  Uint8List pngBytes;
                                                  if (dataObj is Uint8List) {
                                                    pngBytes = dataObj;
                                                  } else if (dataObj
                                                      is List<int>) {
                                                    pngBytes =
                                                        Uint8List.fromList(
                                                          dataObj,
                                                        );
                                                  } else {
                                                    // Attempt to read using dynamic `readNext()` calls
                                                    try {
                                                      final buffer = <int>[];
                                                      final dyn =
                                                          dataObj as dynamic;
                                                      while (true) {
                                                        final chunk = await dyn
                                                            .readNext();
                                                        if (chunk == null) {
                                                          break;
                                                        }
                                                        if (chunk
                                                                is Uint8List &&
                                                            chunk.isEmpty) {
                                                          break;
                                                        }
                                                        if (chunk
                                                                is List<int> &&
                                                            chunk.isEmpty) {
                                                          break;
                                                        }
                                                        if (chunk
                                                            is Uint8List) {
                                                          buffer.addAll(chunk);
                                                        } else if (chunk
                                                            is List<int>) {
                                                          buffer.addAll(chunk);
                                                        } else {
                                                          break;
                                                        }
                                                      }
                                                      try {
                                                        await dyn.close();
                                                      } catch (_) {}
                                                      pngBytes =
                                                          Uint8List.fromList(
                                                            buffer,
                                                          );
                                                    } catch (e) {
                                                      return;
                                                    }
                                                  }

                                                  if (pngBytes.isEmpty) return;

                                                  final image = img.decodePng(
                                                    pngBytes,
                                                  );
                                                  if (image == null) return;

                                                  if (!context.mounted) return;
                                                  final fileName = await showDialog<String>(
                                                    context: context,
                                                    builder: (dialogContext) {
                                                      final controller =
                                                          TextEditingController();
                                                      return AlertDialog(
                                                        title: const Text(
                                                          'Save image as...',
                                                        ),
                                                        content: TextField(
                                                          controller:
                                                              controller,
                                                          decoration:
                                                              const InputDecoration(
                                                                hintText:
                                                                    "Enter filename (without extension)",
                                                              ),
                                                        ),
                                                        actions: [
                                                          TextButton(
                                                            onPressed: () =>
                                                                Navigator.of(
                                                                  dialogContext,
                                                                ).pop(),
                                                            child: const Text(
                                                              'Cancel',
                                                            ),
                                                          ),
                                                          TextButton(
                                                            onPressed: () {
                                                              if (controller
                                                                  .text
                                                                  .isNotEmpty) {
                                                                Navigator.of(
                                                                  dialogContext,
                                                                ).pop(
                                                                  controller
                                                                      .text,
                                                                );
                                                              }
                                                            },
                                                            child: const Text(
                                                              'Save',
                                                            ),
                                                          ),
                                                        ],
                                                      );
                                                    },
                                                  );

                                                  if (fileName != null &&
                                                      fileName.isNotEmpty) {
                                                    final directory =
                                                        await getApplicationDocumentsDirectory();
                                                    final cardbacksDir = Directory(
                                                      '${directory.path}/cardbacks',
                                                    );
                                                    if (!await cardbacksDir
                                                        .exists()) {
                                                      await cardbacksDir.create(
                                                        recursive: true,
                                                      );
                                                    }
                                                    final bmpPath =
                                                        '${cardbacksDir.path}/$fileName.bmp';
                                                    final bmpData = img
                                                        .encodeBmp(image);
                                                    await File(
                                                      bmpPath,
                                                    ).writeAsBytes(bmpData);

                                                    appState.updateConfig(
                                                      'backside',
                                                      bmpPath,
                                                    );

                                                    if (!context.mounted) {
                                                      return;
                                                    }
                                                    ScaffoldMessenger.of(
                                                      context,
                                                    ).showSnackBar(
                                                      SnackBar(
                                                        content: Text(
                                                          'Saved to $bmpPath',
                                                        ),
                                                      ),
                                                    );
                                                  }
                                                },
                                              ),
                                            ],
                                          ),
                                          onTap: () async {
                                            FilePickerResult? result =
                                                await FilePicker.platform
                                                    .pickFiles(
                                                      type: FileType.image,
                                                    );

                                            if (result != null) {
                                              appState.updateConfig(
                                                'backside',
                                                result.files.single.path!,
                                              );
                                            }
                                          },
                                        ),
                                      ],
                                    );
                                  },
                                ),
                              ),
                            ],
                          ),
                        ),
                      )
                    : const SizedBox.shrink(),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class PagePreview extends StatefulWidget {
  final DecklistToPdfCore core;

  const PagePreview({super.key, required this.core});

  @override
  State<PagePreview> createState() => _PagePreviewState();
}

class _PagePreviewState extends State<PagePreview> {
  int _currentPage = 0;
  int _currentSide = 0;
  Map<String, ui.Image> _uiImages = {};
  bool _imagesLoading = true;
  String? _loadingError;

  @override
  void initState() {
    super.initState();
    _loadUiImages();
  }

  @override
  void didUpdateWidget(PagePreview oldWidget) {
    super.didUpdateWidget(oldWidget);
    // If the decklist changes, we might need to reload images
    if (widget.core.decklist != oldWidget.core.decklist) {
      _loadUiImages();
    }
  }

  Future<void> _loadUiImages() async {
    if (!mounted) return;
    setState(() {
      _imagesLoading = true;
      _loadingError = null;
    });

    try {
      // Ensure image cache is populated
      if (widget.core.imageCache.isEmpty) {
        await widget.core.createImageCache();
      }

      final newImages = <String, ui.Image>{};
      final imageCache = widget.core.imageCache;

      for (final key in imageCache.keys) {
        final imgData = imageCache[key];
        if (imgData == null) continue;

        final completer = Completer<ui.Image>();
        ui.decodeImageFromList(img.encodePng(imgData), (ui.Image img) {
          return completer.complete(img);
        });
        newImages[key] = await completer.future;
      }
      if (mounted) {
        setState(() {
          _uiImages = newImages;
          _imagesLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _loadingError = 'Error loading images: $e';
          _imagesLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final core = widget.core;
    final totalPages = ((core.decklist.length + 8) / 9).ceil();
    final isTwoSided = core.conf['two_sided'] == true;

    if (_imagesLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_loadingError != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Text(
            _loadingError!,
            style: const TextStyle(color: Colors.red),
            textAlign: TextAlign.center,
          ),
        ),
      );
    }

    return Column(
      children: [
        Expanded(
          child: Stack(
            alignment: Alignment.center,
            children: [
              InteractiveViewer(
                maxScale: 5.0,
                child: Center(
                  child: AspectRatio(
                    aspectRatio:
                        (core.consts['page_width_px'] as int) /
                        (core.consts['page_height_px'] as int),
                    child: CustomPaint(
                      painter: _PagePainter(
                        core: core,
                        page: _currentPage,
                        side: _currentSide,
                        images: _uiImages,
                      ),
                      child: Container(),
                    ),
                  ),
                ),
              ),
              if (_currentPage > 0)
                Positioned(
                  left: 0,
                  child: GestureDetector(
                    onTap: () => setState(() => _currentPage--),
                    child: Container(
                      color: Colors.black.withValues(alpha: 0.3),
                      height: 300,
                      width: 50,
                      child: const Icon(
                        Icons.arrow_back_ios_new,
                        color: Colors.white,
                        size: 30,
                      ),
                    ),
                  ),
                ),
              if (_currentPage < totalPages - 1)
                Positioned(
                  right: 0,
                  child: GestureDetector(
                    onTap: () => setState(() => _currentPage++),
                    child: Container(
                      color: Colors.black.withValues(alpha: 0.3),
                      height: 300,
                      width: 50,
                      child: const Icon(
                        Icons.arrow_forward_ios,
                        color: Colors.white,
                        size: 30,
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ),
        const Divider(height: 1),
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              IconButton(
                icon: const Icon(Icons.first_page),
                onPressed: totalPages > 1
                    ? () => setState(() {
                        _currentPage = 0;
                      })
                    : null,
              ),
              IconButton(
                icon: const Icon(Icons.chevron_left),
                onPressed: _currentPage > 0
                    ? () => setState(() {
                        _currentPage--;
                      })
                    : null,
              ),
              const SizedBox(width: 16),
              Text('Page ${_currentPage + 1} of $totalPages'),
              const SizedBox(width: 16),
              IconButton(
                icon: const Icon(Icons.chevron_right),
                onPressed: _currentPage < totalPages - 1
                    ? () => setState(() {
                        _currentPage++;
                      })
                    : null,
              ),
              IconButton(
                icon: const Icon(Icons.last_page),
                onPressed: totalPages > 1
                    ? () => setState(() {
                        _currentPage = totalPages - 1;
                      })
                    : null,
              ),
              if (isTwoSided) ...[
                const SizedBox(width: 24),
                const VerticalDivider(),
                const SizedBox(width: 24),
                ChoiceChip(
                  label: const Text('Front'),
                  selected: _currentSide == 0,
                  onSelected: (selected) {
                    if (selected) setState(() => _currentSide = 0);
                  },
                ),
                const SizedBox(width: 8),
                ChoiceChip(
                  label: const Text('Back'),
                  selected: _currentSide == 1,
                  onSelected: (selected) {
                    if (selected) setState(() => _currentSide = 1);
                  },
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }
}

class _PagePainter extends CustomPainter {
  final DecklistToPdfCore core;
  final int page;
  final int side;
  final Map<String, ui.Image> images;

  _PagePainter({
    required this.core,
    required this.page,
    required this.side,
    required this.images,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final consts = core.consts;
    final pageWidthPx = consts['page_width_px'] as int;
    final pageHeightPx = consts['page_height_px'] as int;

    final scaleX = size.width / pageWidthPx;
    final scaleY = size.height / pageHeightPx;
    final scale = scaleX < scaleY ? scaleX : scaleY;

    canvas.save();
    canvas.scale(scale);

    // White background for the page
    canvas.drawRect(
      Rect.fromLTWH(0, 0, pageWidthPx.toDouble(), pageHeightPx.toDouble()),
      Paint()..color = Colors.white,
    );

    // Black background box
    final bgBox = consts['bg_box'] as List<dynamic>?;
    if (bgBox != null && bgBox.length == 4) {
      canvas.drawRect(
        Rect.fromLTRB(
          bgBox[0].toDouble(),
          bgBox[1].toDouble(),
          bgBox[2].toDouble(),
          bgBox[3].toDouble(),
        ),
        Paint()..color = Colors.black,
      );
    }

    // Reference points
    if (core.conf['reference_points'] == true) {
      final markerRects = consts['marker_rects'] as List<dynamic>?;
      if (markerRects != null) {
        for (final rect in markerRects) {
          if (rect is List && rect.length == 4) {
            canvas.drawRect(
              Rect.fromLTWH(
                rect[0].toDouble(),
                rect[1].toDouble(),
                rect[2].toDouble(),
                rect[3].toDouble(),
              ),
              Paint()
                ..color = Colors.white
                ..style = PaintingStyle.stroke
                ..strokeWidth = 1.0 / scale, // Keep stroke width constant
            );
          }
        }
      }
    }

    final cardsPerPage = 9;
    var cardIndexOffset = page * cardsPerPage;

    final isTwoSided = core.conf['two_sided'] == true;
    //final isStagger = core.conf['stagger'] == true;

    for (var row = 0; row < 3; row++) {
      for (var col = 0; col < 3; col++) {
        final cardIndexOnPage = row * 3 + col;
        final overallCardIndex = cardIndexOffset + cardIndexOnPage;

        if (overallCardIndex >= core.decklist.length) break;

        final cardInfo = core.decklist[overallCardIndex];
        String imageKey = 'placeholder'; // default

        if (isTwoSided) {
          // The logic for which card face to show depends on the side of the paper.
          // The physical arrangement on the PDF is handled by `renderPages`.
          // Here, we just need to show the correct face for the selected "side" view.
          if (side == 0) {
            // Front side of paper
            if (cardInfo['two_sided'] && cardInfo['sides'] != null) {
              imageKey = cardInfo['sides'][0]['key'];
            } else {
              imageKey = cardInfo['key'];
            }
          } else {
            // Back side of paper
            if (cardInfo['two_sided'] && cardInfo['sides'] != null) {
              imageKey = cardInfo['sides'][1]['key'];
            } else {
              // For single-sided cards, the back is either custom or default
              imageKey = core.conf['custom_backside'] == true
                  ? 'custom_back'
                  : 'back';
            }
          }
        } else {
          // Single-sided printing
          if (cardInfo['two_sided'] && cardInfo['sides'] != null) {
            imageKey = cardInfo['sides'][0]['key']; // Only show front
          } else {
            imageKey = cardInfo['key'];
          }
        }

        final imageToDraw = images[imageKey];
        final pos = consts['card_positions_px'][row][col] as List<dynamic>;
        final x = pos[0].toDouble();
        final y = pos[1].toDouble();

        if (imageToDraw != null) {
          // The y-position in consts is from the bottom-left, canvas is top-left
          final adjustedY =
              pageHeightPx - y - (consts['card_height_px'] as int);
          canvas.drawImage(
            imageToDraw,
            Offset(x, adjustedY.toDouble()),
            Paint(),
          );
        } else {
          // Draw a placeholder if image not found
          final adjustedY =
              pageHeightPx - y - (consts['card_height_px'] as int);
          canvas.drawRect(
            Rect.fromLTWH(
              x,
              adjustedY.toDouble(),
              (consts['card_width_px'] as int).toDouble(),
              (consts['card_height_px'] as int).toDouble(),
            ),
            Paint()..color = Colors.grey[300]!,
          );
          // You could also draw text here
        }
      }
    }

    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant _PagePainter oldDelegate) {
    return oldDelegate.core != core ||
        oldDelegate.page != page ||
        oldDelegate.side != side ||
        oldDelegate.images != images;
  }
}
