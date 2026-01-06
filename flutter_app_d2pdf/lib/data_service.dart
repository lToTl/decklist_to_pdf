import 'dart:async';
import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'card_data_model.dart';

const String _kCardBox = 'scryfall_cards_box';
Box<CardModel> cardBox = Hive.box<CardModel>(_kCardBox);

class CardDataService {
  static bool isScryfallDownloadComplete = false;

  // --- Initialization and One-Time Save Logic ---

  static Future<void> initializeAndLoadData(
    String rawJsonAssetPath,
    List releaseSchedule,
  ) async {
    // 1. Initialize Hive
    await Hive.initFlutter();

    // 2. Register the generated TypeAdapter BEFORE opening the box
    Hive.registerAdapter(CardModelAdapter());

    // 3. Open the Box
    cardBox = await Hive.openBox<CardModel>(_kCardBox);

    // Check if the data is already saved in the fast binary format
    if (cardBox.isNotEmpty) {
      print('Data already saved to Hive. Skipping JSON parsing.');
      return;
    }

    // Wait for Scryfall download to complete if it's in progress
    while (!isScryfallDownloadComplete) {
      await Future.delayed(const Duration(milliseconds: 100));
    }

    // --- ONE-TIME SLOW PARSING AND FAST BINARY SAVING ---
    print('First run: Loading and parsing large JSON file...');
    // Check if rawJsonAssetPath is valid,
    if (rawJsonAssetPath.isEmpty) {
      throw Exception('Invalid rawJsonAssetPath provided.');
    }
    // a. Load the large JSON file (0.5GB) from assets
    final String rawData = await rootBundle.loadString(rawJsonAssetPath);

    // b. Parse the JSON string into a Dart List
    final List<dynamic> jsonList = json.decode(rawData);

    // c. Prune and map the JSON to your CardModel objects
    final List<CardModel> cards = jsonList
        .map((json) => CardModel.fromJson(json))
        .toList();

    print('JSON parsed and pruned. Total cards: ${cards.length}');

    // d. Save all models to the Hive box in one go (Extremely Fast)
    // The Map ensures each card is stored with a unique, retrievable key (e.g., set-collectorNumber)
    final Map<String, CardModel> cardMap = {
      for (var card in cards) card.appKey: card,
    };

    // Hive handles the fast binary serialization here
    await cardBox.putAll(cardMap);

    print('All data successfully saved to Hive Box as binary.');
  }

  // --- Fast Loading Logic ---

  static Future loadCards() async {
    // This part runs every time the app needs the data (Extremely Fast Load)

    // 1. Re-open the box (it's often already open)
    final Box<CardModel> cardBox = await Hive.openBox<CardModel>(_kCardBox);

    // 2. Get all values (The data is loaded directly from the binary file)
    // This operation is much faster than any JSON or text file parsing.
    if (cardBox.isEmpty) {
      print('No data found in Hive Box. Please initialize first.');
      return false;
    }
    return true;
  }

  static Future<CardModel?> getCardByKey(String key) async {
    return cardBox.get(key);
  }

  static Future<List<CardModel>> getCardsByName(String name) async {
    final Box<CardModel> cardBox = await Hive.openBox<CardModel>(_kCardBox);
    return cardBox.values
        .where((card) => card.name.toLowerCase().contains(name.toLowerCase()))
        .toList();
  }
}
