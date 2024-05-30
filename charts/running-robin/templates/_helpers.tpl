{{/*
Expand the name of the chart.
*/}}
{{- define "running-robin.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "running-robin.fullname" -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- $fullname := printf "%s-%s" .Release.Name $name -}}
{{- $trimmed := trunc 63 $fullname | trimSuffix "-" -}}
{{- if $trimmed | regexFind "[a-zA-Z0-9]$" }}
{{- $trimmed -}}
{{- else }}
{{- $trimmed | trunc 62 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "running-robin.labels" -}}
app.kubernetes.io/name: {{ include "running-robin.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}
