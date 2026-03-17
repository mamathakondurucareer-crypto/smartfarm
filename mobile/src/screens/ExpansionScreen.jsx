/**
 * Expansion — Year 5 milestones, CapEx tracking, readiness score.
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TouchableOpacity, ScrollView, ActivityIndicator,
} from "react-native";
import {
  TrendingUp, Target, DollarSign, CheckCircle, AlertCircle, BarChart3,
} from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import StatGrid from "../components/ui/StatGrid";
import ProgressBar from "../components/ui/ProgressBar";
import { colors, spacing, radius, fontSize } from "../config/theme";
import { api } from "../services/api";
import useAuthStore from "../store/useAuthStore";
import { styles } from "./ExpansionScreen.styles";
import { commonStyles as cs } from "../styles/common";

export default function ExpansionScreen() {
  const token = useAuthStore((s) => s.token);
  const [phases, setPhases] = useState([]);
  const [milestones, setMilestones] = useState([]);
  const [readinessScore, setReadinessScore] = useState(null);
  const [capex, setCapex] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [phasesRes, milestonesRes, readinessRes, capexRes] = await Promise.all([
        api.expansion.phases(token),
        api.expansion.milestones(token),
        api.expansion.readinessScore(token),
        api.expansion.capexBudgetVsActual(token),
      ]);

      setPhases(Array.isArray(phasesRes) ? phasesRes : []);
      setMilestones(Array.isArray(milestonesRes) ? milestonesRes : []);
      setReadinessScore(readinessRes);
      setCapex(capexRes);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Calculate overall milestone progress
  const totalMilestones = milestones.length;
  const completedMilestones = milestones.filter((m) => m.completion_pct >= 100).length;
  const avgProgress =
    totalMilestones > 0 ? milestones.reduce((sum, m) => sum + (m.completion_pct || 0), 0) / totalMilestones : 0;

  const readinessValue = readinessScore?.readiness_score || 0;
  const readinessColor = readinessValue >= 80 ? colors.success : readinessValue >= 60 ? colors.warn : colors.danger;

  const capexBudget = capex?.total_budget || 0;
  const capexSpent = capex?.total_spent || 0;
  const capexUtilization = capexBudget > 0 ? (capexSpent / capexBudget) * 100 : 0;

  const kpiStats = [
    {
      Icon: Target,
      label: "Milestones",
      value: `${completedMilestones}/${totalMilestones}`,
      color: colors.primary,
      sub: `${avgProgress.toFixed(0)}% avg progress`,
    },
    {
      Icon: DollarSign,
      label: "CapEx Utilization",
      value: `${capexUtilization.toFixed(0)}%`,
      color: colors.accent,
      sub: `₹${(capexSpent / 10000000).toFixed(1)}Cr spent`,
    },
    {
      Icon: CheckCircle,
      label: "Readiness Score",
      value: `${readinessValue}%`,
      color: readinessColor,
      sub: "expansion readiness",
    },
  ];

  if (loading) {
    return (
      <ScreenWrapper title="Expansion Tracker">
        <ActivityIndicator size="large" color={colors.primary} style={{ marginTop: 40 }} />
      </ScreenWrapper>
    );
  }

  return (
    <ScreenWrapper title="Expansion Tracker">
      {!!error && <View style={cs.errorBox}><Text style={cs.errorText}>{error}</Text></View>}

      <StatGrid stats={kpiStats} />
      <View style={{ height: spacing.lg }} />

      {/* Milestones Progress */}
      <Card style={cs.cardGap}>
        <SectionHeader Icon={Target} title="Year 5 Milestones" color={colors.primary} />
        {milestones.length === 0 ? (
          <Text style={cs.empty}>No milestones defined.</Text>
        ) : (
          milestones.map((milestone) => (
            <View key={milestone.id} style={styles.milestoneRow}>
              <View>
                <Text style={styles.milestoneName}>{milestone.name || `Milestone ${milestone.id}`}</Text>
                {milestone.due_date && (
                  <Text style={styles.milestoneMeta}>Due: {milestone.due_date}</Text>
                )}
              </View>
              <View style={styles.progressContainer}>
                <ProgressBar
                  value={milestone.completion_pct || 0}
                  color={milestone.completion_pct >= 100 ? colors.success : colors.accent}
                  height={6}
                />
                <Text style={styles.progressText}>{milestone.completion_pct || 0}%</Text>
              </View>
            </View>
          ))
        )}
      </Card>

      <View style={{ height: spacing.lg }} />

      {/* Phases Overview */}
      <Card style={cs.cardGap}>
        <SectionHeader Icon={TrendingUp} title="Project Phases" color={colors.info} />
        {phases.length === 0 ? (
          <Text style={cs.empty}>No phases recorded.</Text>
        ) : (
          phases.map((phase) => (
            <View key={phase.id} style={cs.row}>
              <View style={{ flex: 1 }}>
                <Text style={styles.phaseName}>{phase.name || `Phase ${phase.id}`}</Text>
                <Text style={styles.phaseMeta}>{phase.description || "No description"}</Text>
              </View>
              <View style={{ alignItems: "center" }}>
                <Text style={styles.phaseProgress}>{phase.progress_pct || 0}%</Text>
              </View>
            </View>
          ))
        )}
      </Card>

      <View style={{ height: spacing.lg }} />

      {/* CapEx Summary */}
      {capex && (
        <Card style={cs.cardGap}>
          <SectionHeader Icon={DollarSign} title="CapEx Budget vs Actual" color={colors.accent} />
          <View style={styles.capexRow}>
            <View style={styles.capexCol}>
              <Text style={styles.capexLabel}>Total Budget</Text>
              <Text style={styles.capexValue}>₹{(capex.total_budget / 10000000).toFixed(1)}Cr</Text>
            </View>
            <View style={styles.capexCol}>
              <Text style={styles.capexLabel}>Total Spent</Text>
              <Text style={styles.capexValue}>₹{(capex.total_spent / 10000000).toFixed(1)}Cr</Text>
            </View>
            <View style={styles.capexCol}>
              <Text style={styles.capexLabel}>Remaining</Text>
              <Text style={styles.capexValue}>₹{((capex.total_budget - capex.total_spent) / 10000000).toFixed(1)}Cr</Text>
            </View>
          </View>
          <View style={styles.capexProgressContainer}>
            <ProgressBar value={capexUtilization} color={colors.accent} height={8} />
            <Text style={styles.capexProgressText}>{capexUtilization.toFixed(1)}% Utilized</Text>
          </View>
        </Card>
      )}
    </ScreenWrapper>
  );
}
