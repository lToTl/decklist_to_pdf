//import 'dart:ffi';

//import 'package:flutter/material.dart';
import 'package:hive/hive.dart';

part 'card_data_model.g.dart';

@HiveType(typeId: 5) // Unique Type ID for Deck Model
class Deck extends HiveObject {
  @HiveField(0)
  final object = 'deck'; // Object type
  @HiveField(1)
  final String name; // Name of the deck
  @HiveField(2)
  final String description = ''; // Description of the deck
  @HiveField(3)
  final Map<String, int> cards = {}; // List of card appKeys in the deck
  @HiveField(4)
  final Map<String, Tag> tags = {}; // Map of tag names to Tag objects associated with the deck
  // Constructor to create the Deck object after importing from menu
  Deck({required this.name});
  // Method to add a card to the deck
  void addCard(String appKey, {int quantity = 1}) {
    cards.update(appKey, (value) => value + quantity, ifAbsent: () => quantity);
  }

  // Method to add a tag to the deck
  void addTag(Tag tag) {
    tags[tag.name] = tag;
  }

  // Method to remove a tag from the deck
  void removeTag(String tagName) {
    tags.remove(tagName);
  }

  // factory method to create a Deck from menu input
  factory Deck.fromInput(String name) {
    return Deck(name: name);
  }

  // Method to remove cards in selection from the deck
  void removeCards(List<String> appKeys) {
    cards.removeWhere((key, value) => appKeys.contains(key));
  }

  // Method to remove a card from the deck
  void removeCard(String appKey) {
    cards.remove(appKey);
  }

  // Method to clear all cards from the deck
  void clearDeck() {
    cards.clear();
  }

  // Method to clear all tags from the deck
  void clearTags() {
    tags.clear();
  }

  // Method to get the number of cards in the deck
  int getCardCount() {
    return cards.length;
  }

  // Method to get the number of tags in the deck
  int getTagCount() {
    return tags.length;
  }
}

@HiveType(typeId: 4) // Unique Type ID for Tag Model
class Tag extends HiveObject {
  @HiveField(0)
  final String name; // Name of the tag
  @HiveField(1)
  final String color; // Color associated with the tag
  @HiveField(2)
  final String object = 'tag'; // Object type
  @HiveField(3)
  final Map<String, int> taggedCardsStatus = {}; // Map of card appKeys to their status under this tag

  // Constructor to create the Tag object after parsing the JSON
  Tag({required this.name, required this.color});
  // Factory method to create a Tag from menu input
  factory Tag.fromInput(String name, String color) {
    return Tag(name: name, color: color);
  }
  // Method to add or update a card's status under this tag
  void addOrUpdateCardStatus(String appKey, int status) {
    taggedCardsStatus[appKey] = status;
  }
}

@HiveType(typeId: 3) // Unique Type ID for Set Model
class Set extends HiveObject {
  @HiveField(0)
  final String object = 'set'; // Object type
  @HiveField(1)
  final String id; // Scryfall's unique ID for the set
  @HiveField(2)
  final String code; // Set code
  @HiveField(3)
  final String name; // Name of the set
  @HiveField(4)
  final int setType; // Type of the set
  @HiveField(5)
  final String releasedAt; // Release date of the set
  @HiveField(6)
  final DateTime releaseDate = DateTime.now(); // Parsed release date
  @HiveField(7)
  final String blockCode = ''; // Block code if applicable
  @HiveField(8)
  final String block = ''; // Block name if applicable
  @HiveField(9)
  final String parentSetCode = ''; // Parent set code if applicable
  @HiveField(10)
  final int cardCount = 0; // Number of cards in the set
  @HiveField(11)
  final int printedSize = 0; // Printed size of the set
  @HiveField(12)
  final bool digital = false; // Whether the set is digital
  @HiveField(13)
  final bool foilOnly = false; // Whether the set is foil only
  @HiveField(14)
  final bool nonFoilOnly = false; // Whether the set is non-foil only
  @HiveField(15)
  final String apiUri = ''; // API URI for the set
  @HiveField(16)
  final String iconSvgUri = ''; // URI to the SVG icon of the set
  @HiveField(17)
  final String apiSearchUri = ''; // API search URI for the set for parsing cards in the set
  // Constructor to create the SetModel object after parsing the JSON
  Set({
    required this.id,
    required this.code,
    required this.name,
    required this.setType,
    required this.releasedAt,
  });
}

@HiveType(typeId: 2) // Unique Type ID for Symbol Model
class Symbol extends HiveObject {
  @HiveField(0)
  final String object = 'symbol'; // Object type
  @HiveField(1)
  final String symbol; // The symbol itself
  @HiveField(2)
  final String svgUri = ''; // URI to the SVG image of the symbol
  @HiveField(3)
  final String looseVariant = ''; // Loose variant of the symbol
  @HiveField(4)
  final String english = ''; // English description of the symbol
  @HiveField(5)
  final bool transposeable = false; // Transposable symbol if applicable
  @HiveField(6)
  final bool representsMana; // Whether the symbol represents mana
  @HiveField(7)
  final bool appearsInManaCost; // Whether the symbol appears in mana costs
  @HiveField(8)
  final double manaValue = 0.0; // Numeric mana value of the symbol
  @HiveField(9)
  final bool hybrid = false; // Whether the symbol is a hybrid mana symbol
  @HiveField(10)
  final bool isPhyrexian = false; // Whether the symbol is Phyrexian mana
  @HiveField(11)
  final double cmc = 0.0; // Converted mana cost value of the symbol
  @HiveField(12)
  final bool isFunny = false; // Whether the symbol is a "funny" mana symbol
  @HiveField(13)
  final List<String> colours = []; // Colors associated with the symbol
  @HiveField(14)
  final List<String> gathererAlternates = []; // Gatherer alternate representations of the symbol
  // Constructor to create the Symbol object after parsing the JSON
  Symbol({
    required this.symbol,
    required this.representsMana,
    required this.appearsInManaCost,
  });
}

@HiveType(typeId: 2) // Unique Type ID for RelatedCard Model
class RelatedCard extends HiveObject {
  @HiveField(0)
  final String id; // Scryfall's unique ID
  @HiveField(1)
  final String object = 'related_card'; // Object type
  @HiveField(2)
  final String appKey; // Key representing the card face
  @HiveField(3)
  final String component; // Relationship type one of: token, meld_part, meld_result, combo_piece
  @HiveField(4)
  final String name; // Name of the related card
  @HiveField(5)
  final String typeLine; // Type line of the related card
  @HiveField(6)
  final String uri; // Scryfall URI of the related card
  // Constructor to create the CardFace object after parsing the JSON
  RelatedCard({
    required this.appKey,
    required this.id,
    required this.component,
    required this.name,
    required this.typeLine,
    required this.uri,
  });
}

@HiveType(typeId: 1) // Unique Type ID for CardFase Model
class CardFace extends HiveObject {
  @HiveField(0)
  final String appKey; // Key representing the card face
  @HiveField(1)
  final String artist; // Artist of the card print
  @HiveField(2)
  final double cmc; // Converted mana cost of the card face as a double bc of a joke card that has 0.5 cmc
  @HiveField(3)
  final List<String> colorIndicator = []; // Color indicator of the card face
  @HiveField(4)
  final List<String> colors = []; // Colors of the card face
  @HiveField(5)
  final String defense = ''; // Defense value for battle card faces
  @HiveField(6)
  final String flavorText = ''; // Flavor text of the card face
  @HiveField(7)
  final String illustrationId = ''; // Illustration ID for the card face
  @HiveField(8)
  final Map<String, String> imageUris; // Image URI for the card face
  @HiveField(9)
  final String loyalty; // Loyalty value for planeswalker card faces
  @HiveField(10)
  final String manaCost; // Mana cost of the card face
  @HiveField(11)
  final String name; // Name of the card face
  @HiveField(12)
  final String oracleText; // Oracle text of the card face
  @HiveField(13)
  final String power; // Power value for creature card faces
  @HiveField(14)
  final String printedName = ''; // Printed name of the card face
  @HiveField(15)
  final String printedText = ''; // Printed text of the card face
  @HiveField(16)
  final String printedTypeLine = ''; // Printed type line of the card face
  @HiveField(17)
  final String toughness; // Toughness value for creature card faces
  @HiveField(18)
  final String typeLine; // Type line of the card face
  @HiveField(19)
  final String watermark = ''; // Watermark on the card face

  // Constructor to create the CardFace object after parsing the JSON
  CardFace({
    required this.appKey,
    required this.artist,
    required this.cmc,
    required this.imageUris,
    required this.loyalty,
    required this.manaCost,
    required this.name,
    required this.oracleText,
    required this.power,
    required this.toughness,
    required this.typeLine,
  });
}

@HiveType(typeId: 0) // Unique Type ID for CardModel
class CardModel extends HiveObject {
  // Core fields as for scryfall api
  @HiveField(0)
  final String id; // Scryfall's unique ID
  @HiveField(1)
  final String appKey; // The key used by the app to store files
  @HiveField(2)
  final int cardmarketId; // Cardmarket's unique ID
  @HiveField(3)
  final String object = 'card'; // Object type
  @HiveField(4)
  final String lang; // Language of the card
  @HiveField(5)
  final String layout; // Layout of the card
  @HiveField(6)
  final String oracleId; // Oracle ID
  @HiveField(7)
  final List<int> multiverseIds; // Multiverse ID
  @HiveField(8)
  final String printsSearchUri; // URI for prints search with scryfall api
  @HiveField(9)
  final String rulingsUri; // URI for rulings with scryfall api
  @HiveField(10)
  final String uri; // Scryfall URI
  // Game-related fields
  @HiveField(11)
  final List<RelatedCard> allParts; // All associated cards as RelatedCard objects
  @HiveField(12)
  final List<CardFace> cardFasces;
  @HiveField(13)
  final double cmc; // Converted mana cost of the card
  @HiveField(14)
  final List<String> colorsIdentity; // Colors identity of the card
  @HiveField(15)
  final List<String> colorIndicator; // Color indicator of the card
  @HiveField(16)
  final List<String> colors; // Colors of the card face
  @HiveField(17)
  final String defence; // Defense value for battle cards
  @HiveField(18)
  final int edhrecRank; // EDHREC rank of the card
  @HiveField(19)
  final bool gameChanger; // Whether the card is a game changer
  @HiveField(20)
  final String handModifier; // Hand modifier for the card
  @HiveField(21)
  final List<String> keywords; // Keywords associated with the card
  @HiveField(22)
  final List<int> legalities; // Legalities of the card in various formats
  @HiveField(23)
  final int lifeModifier; // Life modifier for the card
  @HiveField(24)
  final String loyalty; // Loyalty value for planeswalker cards
  @HiveField(25)
  final String manaCost; // Mana cost of the card
  @HiveField(26)
  final String name; // Name of the card
  @HiveField(27)
  final String oracleText;
  @HiveField(28)
  final String typeLine;
  //Print related fields
  @HiveField(29)
  final String artist; // Artist of the card print
  @HiveField(30)
  final List<String> artistsIds; // Artist IDs of the card print
  @HiveField(31)
  final List<bool> attractionLights; // Attraction lights for the card print
  @HiveField(32)
  final bool booster; // Whether the card is in boosters
  @HiveField(33)
  final String borderColor; // Border color of the card print
  @HiveField(34)
  final String cardBackId; // Card back ID of the card print
  @HiveField(35)
  final String collectorNumber; // Collector number of the card print
  @HiveField(36)
  final bool contentWarning; // Whether the card has content warning
  @HiveField(37)
  final bool digital; // Whether the card is digital
  @HiveField(38)
  final String flavorText; // Flavor text of the card print
  @HiveField(39)
  final List<String> frameEffects; // Frame effects of the card print
  @HiveField(40)
  final String frame; // Frame style of the card print
  @HiveField(41)
  final bool fullArt; // Whether the card is full art
  @HiveField(42)
  final List<bool> games; // Games the card is available in: paper, arena, and/or mtgo
  @HiveField(43)
  final bool highResImage; // Whether the card has a high resolution image
  @HiveField(44)
  final String illustrationId; // Illustration ID of the card print
  @HiveField(45)
  final int imageStatus; // Image status of the card print 0: missing, 1: placeholder, 2:lowres , 3: highres_scan
  @HiveField(46)
  final Map<String, String> imageUris; // Image URIs of the card print
  @HiveField(47)
  final bool oversized; // Whether the card is oversized
  @HiveField(48)
  final String printedName; // Localized name of the card print
  @HiveField(49)
  final String printedText; // Localized text of the card print
  @HiveField(50)
  final String printedTypeLine; // Localized type line of the card print
  @HiveField(51)
  final bool promo; // Whether the card is a promo
  @HiveField(52)
  final List<bool> promoTypes; // Promo types of the card print
  @HiveField(53)
  final List<String> purchaseUris; // Purchase URIs for the card print
  @HiveField(54)
  final int rarity; //  This card’s rarity. One of common, uncommon, rare, special, mythic, or bonus.
  @HiveField(55)
  final Map<String, String> relatedUris; // Related URIs for the card print
  @HiveField(56)
  final DateTime releasedAt; // Release date of the card print
  @HiveField(57)
  final bool reprint; // Whether the card is a reprint
  @HiveField(58)
  final String set; // Set code of the card print
  @HiveField(59)
  final String setId; // Scryfall's unique ID for the set this card print belongs to
  @HiveField(60)
  final bool storySpotlight; // Whether the card is a story spotlight
  @HiveField(61)
  final bool textless; // Whether the card is textless
  @HiveField(62)
  final bool variation; // Whether the card is a variation
  @HiveField(63)
  final String variationOf; // If this card is a variation, the ID of the card it is a variation of
  @HiveField(64)
  final int securityStamp; // The security stamp on this card, if any. One of none, oval, triangle, acorn, circle, arena, or heart.
  @HiveField(65)
  final String watermark; // Watermark on the card print
  @HiveField(66)
  // Constructor to create the object after parsing the JSON
  CardModel({
    required this.allParts,
    required this.cardFasces,
    required this.id,
    required this.appKey,
    required this.multiverseIds,
    required this.cardmarketId,
    required this.collectorNumber,
    required this.contentWarning,
    required this.digital,
    required this.lang,
    required this.layout,
    required this.oracleId,
    required this.relatedUris,
    required this.name,
    required this.manaCost,
    required this.oracleText,
    required this.typeLine,
    required this.printsSearchUri,
    required this.rulingsUri,
    required this.uri,
    required this.cmc,
    required this.colorsIdentity,
    required this.colorIndicator,
    required this.colors,
    required this.defence,
    required this.edhrecRank,
    required this.gameChanger,
    required this.handModifier,
    required this.keywords,
    required this.legalities,
    required this.lifeModifier,
    required this.loyalty,
    required this.booster,
    required this.highResImage,
    required this.reprint,
    required this.storySpotlight,
    required this.textless,
    required this.variation,
    required this.setId,
    required this.set,
    required this.flavorText,
    required this.artist,
    required this.artistsIds,
    required this.attractionLights,
    required this.borderColor,
    required this.cardBackId,
    required this.frameEffects,
    required this.frame,
    required this.fullArt,
    required this.games,
    required this.imageStatus,
    required this.imageUris,
    required this.oversized,
    required this.promo,
    required this.promoTypes,
    required this.purchaseUris,
    required this.rarity,
    required this.releasedAt,
    required this.illustrationId,
    required this.printedName,
    required this.printedText,
    required this.printedTypeLine,
    required this.securityStamp,
    required this.variationOf,
    required this.watermark,
  });
  // Factory method to create a CardModel from JSON

  factory CardModel.fromJson(Map<String, dynamic> json) {
    final Map<int, String> formatMap = {
      0: 'standard',
      1: 'future',
      2: 'historic',
      3: 'timeless',
      4: 'gladiator',
      5: 'pioneer',
      6: 'modern',
      7: 'legacy',
      8: 'pauper',
      9: 'vintage',
      10: 'penny',
      11: 'commander',
      12: 'oathbraker',
      13: 'standardbrawl',
      14: 'brawl',
      15: 'alchemy',
      16: 'paupercommander',
      17: 'duel',
      18: 'oldschool',
      19: 'premodern',
      20: 'predh',
    };
    final Map<int, String> legalityMap = {
      0: 'legal',
      1: 'not_legal',
      2: 'restricted',
      3: 'banned',
    };
    final Map<int, String> imageStatusesMap = {
      0: 'missing',
      1: 'placeholder',
      2: 'lowres',
      3: 'highres_scan',
    };
    final Map<int, String> rarityMap = {
      0: 'common',
      1: 'uncommon',
      2: 'rare',
      3: 'special',
      4: 'mythic',
      5: 'bonus',
    };
    final Map<int, String> securityStampMap = {
      0: 'none',
      1: 'oval',
      2: 'triangle',
      3: 'acorn',
      4: 'circle',
      5: 'arena',
      6: 'heart',
    };
    String tAppKey = '${json['set']}_${json['collector_number']}';
    List aLights = json['attraction_lights'] != null
        ? (json['attraction_lights'] as List).cast<int>()
        : [];
    List<bool> aLightsBool = [
      aLights.contains(2),
      aLights.contains(3),
      aLights.contains(4),
      aLights.contains(5),
    ];
    return CardModel(
      id: json['id'] as String,
      allParts: json['all_parts'] != null
          ? (json['all_parts'] as List)
                .map(
                  (e) => RelatedCard(
                    appKey: '${e['set']}_${e['collector_number']}',
                    id: e['id'] as String,
                    component: e['component'] as String,
                    name: e['name'] as String,
                    typeLine: e['type_line'] as String,
                    uri: e['uri'] as String,
                  ),
                )
                .toList()
          : [],
      appKey: tAppKey,
      cardFasces: json['card_faces'] != null
          ? (json['card_faces'] as List)
                .map(
                  (e) => CardFace(
                    appKey:
                        '${tAppKey}_${json['card_faces'].indexOf(e) == 0 ? 'A' : 'B'}',
                    artist: e['artist'] as String,
                    cmc: e['cmc'] != null ? (e['cmc'] as num).toDouble() : 0.0,
                    imageUris: e['image_uris'] != null
                        ? Map<String, String>.from(
                            e['image_uris'] as Map<String, dynamic>,
                          )
                        : {},
                    loyalty: e['loyalty'] != null ? e['loyalty'] as String : '',
                    manaCost: e['mana_cost'] != null
                        ? e['mana_cost'] as String
                        : '',
                    name: e['name'] as String,
                    oracleText: e['oracle_text'] != null
                        ? e['oracle_text'] as String
                        : '',
                    power: e['power'] != null ? e['power'] as String : '',
                    toughness: e['toughness'] != null
                        ? e['toughness'] as String
                        : '',
                    typeLine: e['type_line'] as String,
                  ),
                )
                .toList()
          : [],
      cardmarketId: json['cardmarket_id'] as int,
      multiverseIds: json['multiverse_ids'] != null
          ? json['multiverse_ids'] as List<int>
          : [],
      contentWarning: json['content_warning'] as bool? ?? false,
      digital: json['digital'] as bool? ?? false,
      lang: json['lang'] as String,
      layout: json['layout'] as String,
      oracleId: json['oracle_id'] as String,
      collectorNumber: json['collector_number'] as String,
      name: json['name'] as String,
      colorsIdentity: json['color_identity'] != null
          ? (json['color_identity'] as List).cast<String>()
          : [],
      colorIndicator: json['color_indicator'] != null
          ? (json['color_indicator'] as List).cast<String>()
          : [],
      colors: json['colors'] != null
          ? (json['colors'] as List).cast<String>()
          : [],
      defence: json['defense'] != null ? json['defense'] as String : '',
      edhrecRank: json['edhrec_rank'] as int? ?? 0,
      gameChanger: json['game_changer'] as bool? ?? false,
      handModifier: json['hand_modifier'] != null
          ? json['hand_modifier'] as String
          : '',
      keywords: json['keywords'] != null
          ? (json['keywords'] as List).cast<String>()
          : [],
      legalities: json['legalities'] != null
          ? (json['legalities'] as Map<String, dynamic>).entries
                .map((entry) {
                  String format = entry.key;
                  String legality = entry.value as String;
                  int formatIndex = formatMap.entries
                      .firstWhere(
                        (e) => e.value == format,
                        orElse: () => MapEntry(-1, ''),
                      )
                      .key;
                  int legalityIndex = legalityMap.entries
                      .firstWhere(
                        (e) => e.value == legality,
                        orElse: () => MapEntry(-1, ''),
                      )
                      .key;
                  return formatIndex != -1 && legalityIndex != -1
                      ? legalityIndex
                      : -1;
                })
                .where((index) => index != -1)
                .toList()
          : [],
      manaCost: json['mana_cost'] as String,
      oracleText: json['oracle_text'] as String,
      typeLine: json['type_line'] as String,
      printsSearchUri: json['prints_search_uri'] as String,
      rulingsUri: json['rulings_uri'] as String,
      uri: json['uri'] as String,
      cmc: (json['cmc'] as num).toDouble(),
      flavorText: json['flavor_text'] != null
          ? json['flavor_text'] as String
          : '',
      artist: json['artist'] != null ? json['artist'] as String : '',
      artistsIds: json['artist_ids'] != null
          ? (json['artist_ids'] as List).cast<String>()
          : [],
      attractionLights: aLightsBool,
      lifeModifier: json['life_modifier'] as int? ?? 0,
      loyalty: json['loyalty'] != null ? json['loyalty'] as String : '',
      borderColor: json['border_color'] as String,
      cardBackId: json['card_back_id'] as String,
      frameEffects: json['frame_effects'] != null
          ? (json['frame_effects'] as List).cast<String>()
          : [],
      frame: json['frame'] as String,
      fullArt: json['full_art'] as bool? ?? false,
      games: json['games'] != null
          ? (json['games'] as List).map((e) => e as bool).toList()
          : [],
      imageStatus: json['image_status'] != null
          ? imageStatusesMap.entries
                .firstWhere(
                  (e) => e.value == json['image_status'],
                  orElse: () => MapEntry(0, 'missing'),
                )
                .key
          : 0,
      imageUris: json['image_uris'] != null
          ? Map<String, String>.from(json['image_uris'] as Map<String, dynamic>)
          : {},
      promo: json['promo'] as bool? ?? false,
      promoTypes: json['promo_types'] != null
          ? (json['promo_types'] as List).map((e) => e as bool).toList()
          : [],
      purchaseUris: json['purchase_uris'] != null
          ? (json['purchase_uris'] as Map<String, dynamic>).values
                .map((e) => e as String)
                .toList()
          : [],
      illustrationId: json['illustration_id'] != null
          ? json['illustration_id'] as String
          : '',
      printedName: json['printed_name'] != null
          ? json['printed_name'] as String
          : '',
      printedText: json['printed_text'] != null
          ? json['printed_text'] as String
          : '',
      printedTypeLine: json['printed_type_line'] != null
          ? json['printed_type_line'] as String
          : '',
      oversized: json['oversized'] as bool? ?? false,
      booster: json['booster'] as bool? ?? false,
      highResImage: json['high_res_image'] as bool? ?? false,
      reprint: json['reprint'] as bool? ?? false,
      storySpotlight: json['story_spotlight'] as bool? ?? false,
      textless: json['textless'] as bool? ?? false,
      variation: json['variation'] as bool? ?? false,
      setId: json['set_id'] as String? ?? '',
      set: json['set'] as String? ?? '',
      rarity: json['rarity'] != null
          ? rarityMap.entries
                .firstWhere(
                  (e) => e.value == json['rarity'],
                  orElse: () => MapEntry(0, 'common'),
                )
                .key
          : 0,
      releasedAt: json['released_at'] != null
          ? DateTime.parse(json['released_at'] as String)
          : DateTime.now(),
      relatedUris: json['related_uris'] != null
          ? Map<String, String>.from(
              json['related_uris'] as Map<String, String>,
            )
          : {},
      securityStamp: json['security_stamp'] != null
          ? securityStampMap.entries
                .firstWhere(
                  (e) => e.value == json['security_stamp'],
                  orElse: () => MapEntry(0, 'none'),
                )
                .key
          : 0,
      variationOf: json['variation_of'] != null
          ? json['variation_of'] as String
          : '',
      watermark: json['watermark'] != null ? json['watermark'] as String : '',
    );
  }
}
