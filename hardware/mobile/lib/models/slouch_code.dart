class SlouchCode {
  final bool slouching;
  final double confidence;

  const SlouchCode({
    required this.slouching,
    required this.confidence,
  });

  factory SlouchCode.fromJson(Map<String, dynamic> json) {
    return switch (json) {
      {
        'slouching': bool slouching,
        'confidence': double confidence,
      } =>
        SlouchCode(
          slouching: slouching,
          confidence: confidence,
        ),
      _ => throw const FormatException('Failed to load SlouchCode.'),
    };
  }
}