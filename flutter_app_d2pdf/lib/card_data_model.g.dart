// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'card_data_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class SetAdapter extends TypeAdapter<Set> {
  @override
  final int typeId = 3;

  @override
  Set read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return Set(
      id: fields[1] as String,
      code: fields[2] as String,
      name: fields[3] as String,
      setType: fields[4] as int,
      releasedAt: fields[5] as String,
    );
  }

  @override
  void write(BinaryWriter writer, Set obj) {
    writer
      ..writeByte(18)
      ..writeByte(0)
      ..write(obj.object)
      ..writeByte(1)
      ..write(obj.id)
      ..writeByte(2)
      ..write(obj.code)
      ..writeByte(3)
      ..write(obj.name)
      ..writeByte(4)
      ..write(obj.setType)
      ..writeByte(5)
      ..write(obj.releasedAt)
      ..writeByte(6)
      ..write(obj.releaseDate)
      ..writeByte(7)
      ..write(obj.blockCode)
      ..writeByte(8)
      ..write(obj.block)
      ..writeByte(9)
      ..write(obj.parentSetCode)
      ..writeByte(10)
      ..write(obj.cardCount)
      ..writeByte(11)
      ..write(obj.printedSize)
      ..writeByte(12)
      ..write(obj.digital)
      ..writeByte(13)
      ..write(obj.foilOnly)
      ..writeByte(14)
      ..write(obj.nonFoilOnly)
      ..writeByte(15)
      ..write(obj.apiUri)
      ..writeByte(16)
      ..write(obj.iconSvgUri)
      ..writeByte(17)
      ..write(obj.apiSearchUri);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SetAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class SymbolAdapter extends TypeAdapter<Symbol> {
  @override
  final int typeId = 2;

  @override
  Symbol read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return Symbol(
      symbol: fields[1] as String,
      representsMana: fields[6] as bool,
      appearsInManaCost: fields[7] as bool,
    );
  }

  @override
  void write(BinaryWriter writer, Symbol obj) {
    writer
      ..writeByte(15)
      ..writeByte(0)
      ..write(obj.object)
      ..writeByte(1)
      ..write(obj.symbol)
      ..writeByte(2)
      ..write(obj.svgUri)
      ..writeByte(3)
      ..write(obj.looseVariant)
      ..writeByte(4)
      ..write(obj.english)
      ..writeByte(5)
      ..write(obj.transposeable)
      ..writeByte(6)
      ..write(obj.representsMana)
      ..writeByte(7)
      ..write(obj.appearsInManaCost)
      ..writeByte(8)
      ..write(obj.manaValue)
      ..writeByte(9)
      ..write(obj.hybrid)
      ..writeByte(10)
      ..write(obj.isPhyrexian)
      ..writeByte(11)
      ..write(obj.cmc)
      ..writeByte(12)
      ..write(obj.isFunny)
      ..writeByte(13)
      ..write(obj.colours)
      ..writeByte(14)
      ..write(obj.gathererAlternates);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SymbolAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class RelatedCardAdapter extends TypeAdapter<RelatedCard> {
  @override
  final int typeId = 2;

  @override
  RelatedCard read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return RelatedCard(
      appKey: fields[2] as String,
      id: fields[0] as String,
      component: fields[3] as String,
      name: fields[4] as String,
      typeLine: fields[5] as String,
      uri: fields[6] as String,
    );
  }

  @override
  void write(BinaryWriter writer, RelatedCard obj) {
    writer
      ..writeByte(7)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.object)
      ..writeByte(2)
      ..write(obj.appKey)
      ..writeByte(3)
      ..write(obj.component)
      ..writeByte(4)
      ..write(obj.name)
      ..writeByte(5)
      ..write(obj.typeLine)
      ..writeByte(6)
      ..write(obj.uri);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is RelatedCardAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class CardFaceAdapter extends TypeAdapter<CardFace> {
  @override
  final int typeId = 1;

  @override
  CardFace read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return CardFace(
      appKey: fields[0] as String,
      artist: fields[1] as String,
      cmc: fields[2] as double,
      imageUris: (fields[8] as Map).cast<String, String>(),
      loyalty: fields[9] as String,
      manaCost: fields[10] as String,
      name: fields[11] as String,
      oracleText: fields[12] as String,
      power: fields[13] as String,
      toughness: fields[17] as String,
      typeLine: fields[18] as String,
    );
  }

  @override
  void write(BinaryWriter writer, CardFace obj) {
    writer
      ..writeByte(20)
      ..writeByte(0)
      ..write(obj.appKey)
      ..writeByte(1)
      ..write(obj.artist)
      ..writeByte(2)
      ..write(obj.cmc)
      ..writeByte(3)
      ..write(obj.colorIndicator)
      ..writeByte(4)
      ..write(obj.colors)
      ..writeByte(5)
      ..write(obj.defense)
      ..writeByte(6)
      ..write(obj.flavorText)
      ..writeByte(7)
      ..write(obj.illustrationId)
      ..writeByte(8)
      ..write(obj.imageUris)
      ..writeByte(9)
      ..write(obj.loyalty)
      ..writeByte(10)
      ..write(obj.manaCost)
      ..writeByte(11)
      ..write(obj.name)
      ..writeByte(12)
      ..write(obj.oracleText)
      ..writeByte(13)
      ..write(obj.power)
      ..writeByte(14)
      ..write(obj.printedName)
      ..writeByte(15)
      ..write(obj.printedText)
      ..writeByte(16)
      ..write(obj.printedTypeLine)
      ..writeByte(17)
      ..write(obj.toughness)
      ..writeByte(18)
      ..write(obj.typeLine)
      ..writeByte(19)
      ..write(obj.watermark);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is CardFaceAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class CardModelAdapter extends TypeAdapter<CardModel> {
  @override
  final int typeId = 0;

  @override
  CardModel read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return CardModel(
      allParts: (fields[11] as List).cast<RelatedCard>(),
      cardFasces: (fields[12] as List).cast<CardFace>(),
      id: fields[0] as String,
      appKey: fields[1] as String,
      multiverseIds: (fields[7] as List).cast<int>(),
      cardmarketId: fields[2] as int,
      collectorNumber: fields[35] as String,
      contentWarning: fields[36] as bool,
      digital: fields[37] as bool,
      lang: fields[4] as String,
      layout: fields[5] as String,
      oracleId: fields[6] as String,
      relatedUris: (fields[55] as Map).cast<String, String>(),
      name: fields[26] as String,
      manaCost: fields[25] as String,
      oracleText: fields[27] as String,
      typeLine: fields[28] as String,
      printsSearchUri: fields[8] as String,
      rulingsUri: fields[9] as String,
      uri: fields[10] as String,
      cmc: fields[13] as double,
      colorsIdentity: (fields[14] as List).cast<String>(),
      colorIndicator: (fields[15] as List).cast<String>(),
      colors: (fields[16] as List).cast<String>(),
      defence: fields[17] as String,
      edhrecRank: fields[18] as int,
      gameChanger: fields[19] as bool,
      handModifier: fields[20] as String,
      keywords: (fields[21] as List).cast<String>(),
      legalities: (fields[22] as List).cast<int>(),
      lifeModifier: fields[23] as int,
      loyalty: fields[24] as String,
      booster: fields[32] as bool,
      highResImage: fields[43] as bool,
      reprint: fields[57] as bool,
      storySpotlight: fields[60] as bool,
      textless: fields[61] as bool,
      variation: fields[62] as bool,
      setId: fields[59] as String,
      set: fields[58] as String,
      flavorText: fields[38] as String,
      artist: fields[29] as String,
      artistsIds: (fields[30] as List).cast<String>(),
      attractionLights: (fields[31] as List).cast<bool>(),
      borderColor: fields[33] as String,
      cardBackId: fields[34] as String,
      frameEffects: (fields[39] as List).cast<String>(),
      frame: fields[40] as String,
      fullArt: fields[41] as bool,
      games: (fields[42] as List).cast<bool>(),
      imageStatus: fields[45] as int,
      imageUris: (fields[46] as Map).cast<String, String>(),
      oversized: fields[47] as bool,
      promo: fields[51] as bool,
      promoTypes: (fields[52] as List).cast<bool>(),
      purchaseUris: (fields[53] as List).cast<String>(),
      rarity: fields[54] as int,
      releasedAt: fields[56] as DateTime,
      illustrationId: fields[44] as String,
      printedName: fields[48] as String,
      printedText: fields[49] as String,
      printedTypeLine: fields[50] as String,
      securityStamp: fields[64] as int,
      variationOf: fields[63] as String,
      watermark: fields[65] as String,
    );
  }

  @override
  void write(BinaryWriter writer, CardModel obj) {
    writer
      ..writeByte(66)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.appKey)
      ..writeByte(2)
      ..write(obj.cardmarketId)
      ..writeByte(3)
      ..write(obj.object)
      ..writeByte(4)
      ..write(obj.lang)
      ..writeByte(5)
      ..write(obj.layout)
      ..writeByte(6)
      ..write(obj.oracleId)
      ..writeByte(7)
      ..write(obj.multiverseIds)
      ..writeByte(8)
      ..write(obj.printsSearchUri)
      ..writeByte(9)
      ..write(obj.rulingsUri)
      ..writeByte(10)
      ..write(obj.uri)
      ..writeByte(11)
      ..write(obj.allParts)
      ..writeByte(12)
      ..write(obj.cardFasces)
      ..writeByte(13)
      ..write(obj.cmc)
      ..writeByte(14)
      ..write(obj.colorsIdentity)
      ..writeByte(15)
      ..write(obj.colorIndicator)
      ..writeByte(16)
      ..write(obj.colors)
      ..writeByte(17)
      ..write(obj.defence)
      ..writeByte(18)
      ..write(obj.edhrecRank)
      ..writeByte(19)
      ..write(obj.gameChanger)
      ..writeByte(20)
      ..write(obj.handModifier)
      ..writeByte(21)
      ..write(obj.keywords)
      ..writeByte(22)
      ..write(obj.legalities)
      ..writeByte(23)
      ..write(obj.lifeModifier)
      ..writeByte(24)
      ..write(obj.loyalty)
      ..writeByte(25)
      ..write(obj.manaCost)
      ..writeByte(26)
      ..write(obj.name)
      ..writeByte(27)
      ..write(obj.oracleText)
      ..writeByte(28)
      ..write(obj.typeLine)
      ..writeByte(29)
      ..write(obj.artist)
      ..writeByte(30)
      ..write(obj.artistsIds)
      ..writeByte(31)
      ..write(obj.attractionLights)
      ..writeByte(32)
      ..write(obj.booster)
      ..writeByte(33)
      ..write(obj.borderColor)
      ..writeByte(34)
      ..write(obj.cardBackId)
      ..writeByte(35)
      ..write(obj.collectorNumber)
      ..writeByte(36)
      ..write(obj.contentWarning)
      ..writeByte(37)
      ..write(obj.digital)
      ..writeByte(38)
      ..write(obj.flavorText)
      ..writeByte(39)
      ..write(obj.frameEffects)
      ..writeByte(40)
      ..write(obj.frame)
      ..writeByte(41)
      ..write(obj.fullArt)
      ..writeByte(42)
      ..write(obj.games)
      ..writeByte(43)
      ..write(obj.highResImage)
      ..writeByte(44)
      ..write(obj.illustrationId)
      ..writeByte(45)
      ..write(obj.imageStatus)
      ..writeByte(46)
      ..write(obj.imageUris)
      ..writeByte(47)
      ..write(obj.oversized)
      ..writeByte(48)
      ..write(obj.printedName)
      ..writeByte(49)
      ..write(obj.printedText)
      ..writeByte(50)
      ..write(obj.printedTypeLine)
      ..writeByte(51)
      ..write(obj.promo)
      ..writeByte(52)
      ..write(obj.promoTypes)
      ..writeByte(53)
      ..write(obj.purchaseUris)
      ..writeByte(54)
      ..write(obj.rarity)
      ..writeByte(55)
      ..write(obj.relatedUris)
      ..writeByte(56)
      ..write(obj.releasedAt)
      ..writeByte(57)
      ..write(obj.reprint)
      ..writeByte(58)
      ..write(obj.set)
      ..writeByte(59)
      ..write(obj.setId)
      ..writeByte(60)
      ..write(obj.storySpotlight)
      ..writeByte(61)
      ..write(obj.textless)
      ..writeByte(62)
      ..write(obj.variation)
      ..writeByte(63)
      ..write(obj.variationOf)
      ..writeByte(64)
      ..write(obj.securityStamp)
      ..writeByte(65)
      ..write(obj.watermark);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is CardModelAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
