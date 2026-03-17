/**
 * HR Module — attendance, leave requests, payroll, headcount by department.
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TouchableOpacity, ScrollView, ActivityIndicator,
} from "react-native";
import {
  Users, User, Calendar, DollarSign, BarChart3, CheckCircle, AlertCircle,
} from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import StatGrid from "../components/ui/StatGrid";
import BarChartCard from "../components/charts/BarChartCard";
import Badge from "../components/ui/Badge";
import { colors, spacing, chartColors } from "../config/theme";
import { api } from "../services/api";
import useAuthStore from "../store/useAuthStore";
import { styles } from "./HRScreen.styles";
import { commonStyles as cs } from "../styles/common";

export default function HRScreen() {
  const token = useAuthStore((s) => s.token);
  const [attendance, setAttendance] = useState(null);
  const [leaveRequests, setLeaveRequests] = useState([]);
  const [payrollRun, setPayrollRun] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      // Fetch attendance (today)
      const todayDate = new Date().toISOString().split("T")[0];
      const attendRes = await api.hr.attendance(token, `?date=${todayDate}`);
      setAttendance(attendRes);

      // Fetch pending leave requests
      const leaveRes = await api.hr.leaveRequests(token, "?status=pending");
      setLeaveRequests(Array.isArray(leaveRes) ? leaveRes : []);

      // Fetch latest payroll run
      const payrollRes = await api.hr.payrollRuns(token);
      if (Array.isArray(payrollRes) && payrollRes.length > 0) {
        setPayrollRun(payrollRes[0]);
      }

      // Fetch headcount by department
      const deptRes = await api.hr.departmentHeadcount(token);
      const deptData = Array.isArray(deptRes) ? deptRes : [];
      setDepartments(deptData);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const presentCount = attendance?.present ?? 0;
  const absentCount = attendance?.absent ?? 0;
  const onLeaveCount = attendance?.on_leave ?? 0;
  const totalStaff = presentCount + absentCount + onLeaveCount;

  const kpiStats = [
    {
      Icon: CheckCircle,
      label: "Present Today",
      value: String(presentCount),
      color: colors.success,
      sub: `of ${totalStaff} staff`,
    },
    {
      Icon: AlertCircle,
      label: "Absent",
      value: String(absentCount),
      color: colors.danger,
      sub: "today",
    },
    {
      Icon: Calendar,
      label: "On Leave",
      value: String(onLeaveCount),
      color: colors.warn,
      sub: "approved",
    },
    {
      Icon: DollarSign,
      label: "Pending Approvals",
      value: String(leaveRequests.length),
      color: colors.info,
      sub: "leave requests",
    },
  ];

  // Department headcount chart
  const deptLabels = departments.map((d) => d.dept_name || "");
  const deptCounts = departments.map((d) => d.headcount || 0);

  // Payroll summary
  const payrollStats = payrollRun
    ? [
        { Icon: DollarSign, label: "Last Payroll", value: new Date(payrollRun.run_date).toLocaleDateString(), color: colors.primary },
        { Icon: BarChart3, label: "Total Gross", value: `₹${(payrollRun.total_gross / 100000).toFixed(1)}L`, color: colors.accent },
        { Icon: BarChart3, label: "Total Net", value: `₹${(payrollRun.total_net / 100000).toFixed(1)}L`, color: colors.info },
      ]
    : [];

  if (loading) {
    return (
      <ScreenWrapper title="HR Management">
        <ActivityIndicator size="large" color={colors.primary} style={{ marginTop: 40 }} />
      </ScreenWrapper>
    );
  }

  return (
    <ScreenWrapper title="HR Management">
      {!!error && <View style={cs.errorBox}><Text style={cs.errorText}>{error}</Text></View>}

      <StatGrid stats={kpiStats} />
      <View style={{ height: spacing.lg }} />

      {/* Payroll Summary */}
      {payrollStats.length > 0 && (
        <>
          <StatGrid stats={payrollStats} />
          <View style={{ height: spacing.lg }} />
        </>
      )}

      {/* Department Headcount Chart */}
      {deptLabels.length > 0 && (
        <>
          <BarChartCard
            Icon={BarChart3}
            title="Headcount by Department"
            color={colors.info}
            labels={deptLabels}
            data={deptCounts}
            yLabel="Employees"
            height={240}
          />
          <View style={{ height: spacing.lg }} />
        </>
      )}

      {/* Leave Requests Pending */}
      <Card style={cs.cardGap}>
        <SectionHeader Icon={Calendar} title={`Leave Requests (${leaveRequests.length} pending)`} color={colors.warn} />
        {leaveRequests.length === 0 ? (
          <Text style={cs.empty}>No pending leave requests.</Text>
        ) : (
          leaveRequests.slice(0, 10).map((req) => (
            <View key={req.id} style={cs.row}>
              <View style={{ flex: 1 }}>
                <Text style={styles.empName}>{req.employee_name || `EMP-${req.employee_id}`}</Text>
                <Text style={styles.empMeta}>{req.leave_type} • {req.duration_days} days</Text>
                <Text style={styles.empMeta}>
                  {req.from_date} to {req.to_date}
                </Text>
              </View>
              <Badge label={req.status || "pending"} color={colors.warn} />
            </View>
          ))
        )}
      </Card>
    </ScreenWrapper>
  );
}
