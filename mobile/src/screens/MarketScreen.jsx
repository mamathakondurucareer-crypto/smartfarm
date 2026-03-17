import React from "react";
import { View, Text } from "react-native";
import { Truck, MapPin, BarChart3 } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import DataTable     from "../components/ui/DataTable";
import Badge         from "../components/ui/Badge";
import BarChartCard  from "../components/charts/BarChartCard";
import { colors, spacing, fontSize } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";
import { styles } from "./MarketScreen.styles";
import { commonStyles as cs } from "../styles/common";

const CITIES = [
  { key: "hyderabad",  name: "Hyderabad",  dist: "400 km", share: "35%" },
  { key: "chennai",    name: "Chennai",    dist: "180 km", share: "25%" },
  { key: "vijayawada", name: "Vijayawada", dist: "280 km", share: "15%" },
  { key: "kadapa",     name: "Kadapa",     dist: "200 km", share: "10%" },
  { key: "nellore",    name: "Nellore",    dist: "15 km",  share: "15%" },
];

const TREND_LABELS = { up: "↑ Up", down: "↓ Down", stable: "→ Stable" };
const TREND_COLORS = { up: colors.primary, down: colors.danger, stable: colors.accent };

export default function MarketScreen() {
  const markets = useFarmStore((s) => s.farm.markets);

  const tableHeaders = ["City", "Dist", "Murrel", "Rohu", "Tomato", "Chilli", "Trend"];
  const tableRows    = CITIES.map((c) => {
    const data = markets[c.key];
    return [
      <Text style={{ fontWeight: "700", color: colors.market }}>{c.name}</Text>,
      c.dist,
      `₹${data.lastPrice.murrel}`,
      `₹${data.lastPrice.rohu}`,
      `₹${data.lastPrice.tomato}`,
      `₹${data.lastPrice.chilli}`,
      <Badge label={TREND_LABELS[data.trend]} color={TREND_COLORS[data.trend]} />,
    ];
  });

  return (
    <ScreenWrapper title="Markets">
      <Card>
        <SectionHeader Icon={MapPin} title="Five-City Market Prices (₹/kg)" color={colors.market} />
        <DataTable headers={tableHeaders} rows={tableRows} />
      </Card>

      <View style={cs.gap} />

      <BarChartCard
        Icon={BarChart3}
        title="Murrel Price Comparison"
        color={colors.fish}
        labels={CITIES.map((c) => c.name.substring(0, 5))}
        data={CITIES.map((c) => markets[c.key].lastPrice.murrel)}
        yLabel="₹"
        height={200}
      />

      <View style={cs.gap} />

      <BarChartCard
        Icon={Truck}
        title="Rohu Price Comparison"
        color={colors.primary}
        labels={CITIES.map((c) => c.name.substring(0, 5))}
        data={CITIES.map((c) => markets[c.key].lastPrice.rohu)}
        yLabel="₹"
        height={200}
      />
    </ScreenWrapper>
  );
}

