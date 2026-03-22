/**
 * Role Management screen — admin only.
 *
 * View all roles (predefined + custom), edit their screen access,
 * and create custom roles with fine-grained permissions.
 */
import React, { useState, useMemo } from "react";
import {
  View, Text, TouchableOpacity, ScrollView,
  Modal, TextInput, Switch, ActivityIndicator,
} from "react-native";
import {
  Shield, Plus, Edit2, Trash2, RotateCcw,
  ChevronDown, ChevronRight, X, Check,
} from "lucide-react-native";
import ScreenWrapper  from "../components/layout/ScreenWrapper";
import Card           from "../components/ui/Card";
import SectionHeader  from "../components/ui/SectionHeader";
import Badge          from "../components/ui/Badge";
import { colors, spacing, fontSize, radius } from "../config/theme";
import { ROLES, ROLE_META, SCREEN_ACCESS } from "../config/permissions";
import { SCREENS, SECTIONS }               from "../config/navigation";
import useRolesStore  from "../store/useRolesStore";
import { commonStyles as cs }              from "../styles/common";
import { styles }                          from "./RolesScreen.styles";

// ── Helpers ───────────────────────────────────────────────────────────────────

const DEFAULT_CUSTOM_COLOR = "#26A69A";

const PREDEFINED = Object.keys(ROLES);

/** All screen names grouped by section. */
const SCREEN_GROUPS = SECTIONS.map((sec) => ({
  ...sec,
  screens: SCREENS.filter((s) => s.section === sec.key),
}));

/** Initial screen list for a predefined role from static config. */
function defaultScreensFor(roleName) {
  const upper = (roleName || "").toUpperCase();
  return SCREENS.map((s) => s.name).filter((name) => {
    const allowed = SCREEN_ACCESS[name];
    if (!allowed) return true;
    return allowed.includes(upper);
  });
}

// ── Sub-components ────────────────────────────────────────────────────────────

function RoleBadge({ label, color, size = "sm" }) {
  return (
    <View style={[styles.roleBadge, { backgroundColor: color + "22", borderColor: color + "55" }]}>
      <Text style={[styles.roleBadgeText, { color, fontSize: size === "lg" ? fontSize.md : fontSize.xs }]}>
        {label}
      </Text>
    </View>
  );
}

function ScreenToggle({ screen, checked, onToggle }) {
  return (
    <TouchableOpacity
      style={styles.toggleRow}
      onPress={() => onToggle(screen.name)}
      activeOpacity={0.7}
    >
      <View style={[styles.screenIcon, { backgroundColor: screen.color + "22" }]}>
        <screen.Icon size={12} color={screen.color} />
      </View>
      <Text style={styles.screenLabel}>{screen.label}</Text>
      <Switch
        value={checked}
        onValueChange={() => onToggle(screen.name)}
        trackColor={{ false: colors.border, true: colors.primary + "88" }}
        thumbColor={checked ? colors.primary : colors.textMuted}
        style={styles.switch}
      />
    </TouchableOpacity>
  );
}

function SectionToggleGroup({ section, selectedScreens, onToggle }) {
  const [open, setOpen] = useState(true);
  const all = section.screens.every((s) => selectedScreens.includes(s.name));

  const toggleAll = () => {
    if (all) {
      section.screens.forEach((s) => {
        if (selectedScreens.includes(s.name)) onToggle(s.name);
      });
    } else {
      section.screens.forEach((s) => {
        if (!selectedScreens.includes(s.name)) onToggle(s.name);
      });
    }
  };

  return (
    <View style={styles.sectionGroup}>
      <TouchableOpacity style={styles.sectionGroupHeader} onPress={() => setOpen((v) => !v)} activeOpacity={0.7}>
        {open ? <ChevronDown size={14} color={colors.textDim} /> : <ChevronRight size={14} color={colors.textDim} />}
        <Text style={styles.sectionGroupLabel}>{section.label}</Text>
        <TouchableOpacity onPress={toggleAll} style={styles.allBtn} activeOpacity={0.7}>
          <Text style={[styles.allBtnText, all && styles.allBtnActive]}>
            {all ? "Deselect all" : "Select all"}
          </Text>
        </TouchableOpacity>
      </TouchableOpacity>
      {open && section.screens.map((sc) => (
        <ScreenToggle
          key={sc.name}
          screen={sc}
          checked={selectedScreens.includes(sc.name)}
          onToggle={onToggle}
        />
      ))}
    </View>
  );
}

// ── Role card ─────────────────────────────────────────────────────────────────

function RoleCard({ role, onEdit, onDelete, onReset, isCustom, hasOverride }) {
  const meta = ROLE_META[role.name] ?? { label: role.name, color: role.color ?? colors.textDim, description: "" };
  const screenCount = role.screens.length;
  const color = isCustom ? (role.color ?? DEFAULT_CUSTOM_COLOR) : meta.color;

  return (
    <View style={styles.roleCard}>
      <View style={styles.roleCardLeft}>
        <RoleBadge label={isCustom ? role.label : meta.label} color={color} />
        <Text style={styles.roleDesc}>{isCustom ? role.description : meta.description}</Text>
        <Text style={styles.roleScreenCount}>{screenCount} screen{screenCount !== 1 ? "s" : ""}</Text>
      </View>
      <View style={styles.roleCardActions}>
        {hasOverride && !isCustom && (
          <TouchableOpacity style={styles.iconBtn} onPress={onReset} hitSlop={{ top: 8, right: 8, bottom: 8, left: 8 }}>
            <RotateCcw size={14} color={colors.textMuted} />
          </TouchableOpacity>
        )}
        <TouchableOpacity style={styles.iconBtn} onPress={onEdit} hitSlop={{ top: 8, right: 8, bottom: 8, left: 8 }}>
          <Edit2 size={14} color={colors.info} />
        </TouchableOpacity>
        {isCustom && (
          <TouchableOpacity style={styles.iconBtn} onPress={onDelete} hitSlop={{ top: 8, right: 8, bottom: 8, left: 8 }}>
            <Trash2 size={14} color={colors.danger} />
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

// ── Edit / Create modal ────────────────────────────────────────────────────────

const COLOR_OPTIONS = [
  "#0288D1", "#2E7D32", "#F57F17", "#558B2F", "#6A1B9A",
  "#00695C", "#1565C0", "#FF7043", "#FFA726", "#8D6E63",
  "#E53935", "#5E35B1", "#00897B", "#D81B60", "#43A047",
];

function EditRoleModal({ visible, onClose, role, isCustom, onSave, saving }) {
  const initialScreens = useMemo(() => role?.screens ?? [], [role]);
  const [label, setLabel]       = useState(role?.label ?? "");
  const [desc, setDesc]         = useState(role?.description ?? "");
  const [color, setColor]       = useState(role?.color ?? DEFAULT_CUSTOM_COLOR);
  const [screens, setScreens]   = useState(initialScreens);
  const [nameError, setNameErr] = useState("");

  // Sync when role changes
  React.useEffect(() => {
    if (visible) {
      setLabel(role?.label ?? "");
      setDesc(role?.description ?? "");
      setColor(role?.color ?? DEFAULT_CUSTOM_COLOR);
      setScreens(role?.screens ?? []);
      setNameErr("");
    }
  }, [visible, role]);

  const toggleScreen = (name) => {
    setScreens((prev) =>
      prev.includes(name) ? prev.filter((s) => s !== name) : [...prev, name]
    );
  };

  const handleSave = () => {
    if (isCustom && !label.trim()) { setNameErr("Role name is required."); return; }
    onSave({ label: label.trim(), description: desc.trim(), color, screens });
  };

  const roleLabel = isCustom ? label : (ROLE_META[role?.name]?.label ?? role?.name ?? "");
  const roleColor = isCustom ? color : (ROLE_META[role?.name]?.color ?? colors.primary);

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <View style={cs.modalOverlay}>
        <View style={[cs.modalContent, styles.editModal]}>
          {/* Header */}
          <View style={styles.modalHeader}>
            <View style={styles.modalTitleRow}>
              <Shield size={16} color={roleColor} />
              <Text style={cs.modalTitle} numberOfLines={1}>
                {role ? `Edit: ${roleLabel}` : "Create Role"}
              </Text>
            </View>
            <TouchableOpacity onPress={onClose} hitSlop={{ top: 8, right: 8, bottom: 8, left: 8 }}>
              <X size={18} color={colors.textDim} />
            </TouchableOpacity>
          </View>

          <ScrollView showsVerticalScrollIndicator={false}>
            {/* Custom role fields */}
            {isCustom && (
              <>
                {!!nameError && (
                  <View style={cs.errorBox}><Text style={cs.errorText}>{nameError}</Text></View>
                )}
                <Text style={cs.label}>Role Name *</Text>
                <TextInput
                  style={cs.input}
                  value={label}
                  onChangeText={setLabel}
                  placeholder="e.g. Harvest Team"
                  placeholderTextColor={colors.textMuted}
                  autoCapitalize="words"
                />
              </>
            )}

            <Text style={cs.label}>Description</Text>
            <TextInput
              style={[cs.input, styles.descInput]}
              value={desc}
              onChangeText={setDesc}
              placeholder="What does this role do?"
              placeholderTextColor={colors.textMuted}
              multiline
            />

            {/* Color picker (custom only) */}
            {isCustom && (
              <>
                <Text style={cs.label}>Accent Color</Text>
                <View style={styles.colorRow}>
                  {COLOR_OPTIONS.map((c) => (
                    <TouchableOpacity
                      key={c}
                      style={[styles.colorDot, { backgroundColor: c }, color === c && styles.colorDotActive]}
                      onPress={() => setColor(c)}
                      activeOpacity={0.8}
                    >
                      {color === c && <Check size={10} color="#fff" />}
                    </TouchableOpacity>
                  ))}
                </View>
              </>
            )}

            {/* Screen access toggles */}
            <Text style={[cs.label, { marginTop: spacing.lg }]}>Screen Access</Text>
            <Text style={styles.screenHint}>
              {screens.length} of {SCREENS.length} screens enabled
            </Text>

            {SCREEN_GROUPS.map((group) => (
              <SectionToggleGroup
                key={group.key}
                section={group}
                selectedScreens={screens}
                onToggle={toggleScreen}
              />
            ))}

            {/* Save */}
            <TouchableOpacity
              style={[styles.saveBtn, { backgroundColor: roleColor }, saving && { opacity: 0.6 }]}
              onPress={handleSave}
              disabled={saving}
              activeOpacity={0.85}
            >
              {saving
                ? <ActivityIndicator size="small" color="#fff" />
                : <Text style={styles.saveBtnText}>Save Changes</Text>}
            </TouchableOpacity>
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
}

// ── Main screen ───────────────────────────────────────────────────────────────

export default function RolesScreen() {
  const { roleOverrides, customRoles, setRoleOverride, resetRoleOverride,
          addCustomRole, updateCustomRole, deleteCustomRole } = useRolesStore();

  const [editTarget, setEditTarget] = useState(null);   // { name, isCustom }
  const [creating, setCreating]     = useState(false);
  const [saving, setSaving]         = useState(false);

  // Build role list for rendering
  const predefinedList = PREDEFINED.map((name) => {
    const meta = ROLE_META[name] ?? { label: name, color: colors.textDim, description: "" };
    const screens = roleOverrides[name] ?? defaultScreensFor(name);
    return { name, label: meta.label, color: meta.color, description: meta.description, screens };
  });

  const customList = customRoles.map((r) => ({
    ...r,
    screens: r.screens ?? [],
  }));

  // Compute edit target data
  const editData = useMemo(() => {
    if (!editTarget) return null;
    if (editTarget.isCustom) {
      return customList.find((r) => r.name === editTarget.name) ?? null;
    }
    return predefinedList.find((r) => r.name === editTarget.name) ?? null;
  }, [editTarget, customRoles, roleOverrides]);

  const openEdit = (name, isCustom) => setEditTarget({ name, isCustom });
  const closeEdit = () => { setEditTarget(null); setCreating(false); };

  const handleSave = async (data) => {
    setSaving(true);
    try {
      if (creating) {
        const roleName = data.label.toUpperCase().replace(/\s+/g, "_");
        await addCustomRole({ name: roleName, ...data });
      } else if (editTarget?.isCustom) {
        await updateCustomRole(editTarget.name, data);
      } else if (editTarget) {
        await setRoleOverride(editTarget.name, data.screens);
        // Also persist description override if changed
        if (data.description !== (ROLE_META[editTarget.name]?.description ?? "")) {
          await setRoleOverride(editTarget.name + "_desc", data.description);
        }
      }
      closeEdit();
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async (name) => {
    await resetRoleOverride(name);
    await resetRoleOverride(name + "_desc");
  };

  const handleDelete = async (name) => {
    await deleteCustomRole(name);
  };

  // Modal data
  const modalRole = creating
    ? { label: "", description: "", color: DEFAULT_CUSTOM_COLOR, screens: [] }
    : editData;

  return (
    <ScreenWrapper title="Role Management">
      {/* Top bar */}
      <View style={cs.topRow}>
        <Text style={cs.count}>
          {predefinedList.length + customList.length} roles configured
        </Text>
        <TouchableOpacity style={styles.addBtn} onPress={() => setCreating(true)} activeOpacity={0.8}>
          <Plus size={14} color={colors.bg} />
          <Text style={styles.addBtnText}>New Role</Text>
        </TouchableOpacity>
      </View>

      {/* Predefined roles */}
      <Card style={styles.cardGap}>
        <SectionHeader Icon={Shield} title="Predefined Roles" color={colors.info} />
        <Text style={styles.cardHint}>
          Edit screen access for any predefined role. Use the reset icon to restore defaults.
        </Text>
        {predefinedList.map((role) => (
          <RoleCard
            key={role.name}
            role={role}
            isCustom={false}
            hasOverride={!!roleOverrides[role.name]}
            onEdit={() => openEdit(role.name, false)}
            onReset={() => handleReset(role.name)}
          />
        ))}
      </Card>

      {/* Custom roles */}
      {customList.length > 0 && (
        <Card>
          <SectionHeader Icon={Shield} title="Custom Roles" color={colors.accent} />
          <Text style={styles.cardHint}>
            Roles created by your organisation. These can be fully edited or deleted.
          </Text>
          {customList.map((role) => (
            <RoleCard
              key={role.name}
              role={role}
              isCustom
              hasOverride={false}
              onEdit={() => openEdit(role.name, true)}
              onDelete={() => handleDelete(role.name)}
            />
          ))}
        </Card>
      )}

      {/* Edit / Create Modal */}
      <EditRoleModal
        visible={!!editTarget || creating}
        onClose={closeEdit}
        role={modalRole}
        isCustom={creating || (editTarget?.isCustom ?? false)}
        onSave={handleSave}
        saving={saving}
      />
    </ScreenWrapper>
  );
}
