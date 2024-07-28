class SlouchCode {
  final bool is_slouching;
  final double confidence;

  const SlouchCode({
    required this.is_slouching,
    required this.confidence,
  });

  factory SlouchCode.fromJson(Map<String, dynamic> json) {
    return switch (json) {
      {
        'is_slouching': bool is_slouching,
        'confidence': double confidence,
      } =>
        SlouchCode(
          is_slouching: is_slouching,
          confidence: confidence,
        ),
      _ => throw const FormatException('Failed to load SlouchCode.'),
    };
  }
}