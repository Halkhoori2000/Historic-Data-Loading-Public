# HDLP

> Production code lives in a private repository. This repo showcases the **architecture**, **design standards**, **documentation**, and **runnable examples** behind the **Historic Data Loading Framework** used for ingesting historic and manually managed files into a governed analytics platform.

---

## Table of Contents
- [Overview](#overview)
- [Purpose](#purpose)
- [What This Repository Shows](#what-this-repository-shows)
- [High-Level Architecture](#high-level-architecture)
- [Lakehouse Layer Design](#lakehouse-layer-design)
- [Manual Files Fast Path](#manual-files-fast-path)
- [ETL Framework Flow](#etl-framework-flow)
- [Detailed ETL Components](#detailed-etl-components)
- [Schema Drift Handling](#schema-drift-handling)
- [Invalid XML and Bad File Handling](#invalid-xml-and-bad-file-handling)
- [Example Test Pack Included in This Repo](#example-test-pack-included-in-this-repo)
- [Repository Structure](#repository-structure)
- [Setup and Usage](#setup-and-usage)
- [How to Extend the Framework](#how-to-extend-the-framework)
- [Metadata and Governance](#metadata-and-governance)
- [Testing Strategy](#testing-strategy)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)
- [Roadmap](#roadmap)

---

## Overview

This framework is built to process data from both:

- **source systems** using **full load** ingestion, and
- **manual files** such as **Excel**, **CSV**, **XML**, and other business-managed extracts.

The framework standardizes ingestion into a governed **Bronze → Silver → Gold** lakehouse pattern, followed by a **semantic layer** for reporting tools such as **Power BI**, **SQL**, and other analytics consumers.

It is especially useful when files are messy or inconsistent, for example:

- changing column names across months
- columns being added or removed over time
- different sheet names in each workbook
- duplicate or unnamed columns
- headers starting on different rows or columns
- repeated headers inside the file
- malformed XML or invalid file structure

---

## Purpose

The goal of this framework is to:

- build a strong data foundation for reporting and analytics
- enable efficient, governed, and reliable access to data
- maximize shareholder value by using data to support decision-making

---

## What This Repository Shows

This is a **showcase repository**. The production code is private, but this repo demonstrates the overall design and operating model.

### Included
- high-level architecture
- ETL framework design
- Bronze, Silver, and Gold responsibilities
- example schema-drift test pack
- configuration-driven ingestion patterns
- file and sheet mapping examples
- testing and troubleshooting guidance
- standards for metadata, DQ, and extensibility

### Not Included
- production credentials
- private business logic
- confidential data models
- production deployment assets

---

## High-Level Architecture

```mermaid
flowchart LR
  subgraph SRC[Sources]
    direction TB
    SYS[🖥️ Source Systems]
    MF[📄 Manual Files]
  end

  subgraph ING[Ingestion]
    direction TB
    CDC[🔁 CDC / Trigger Based]
    BATCH[🧭 Batch / Scheduled]
  end

  subgraph LAKE[ADLS + Lakehouse]
    direction LR
    BRZ[🥉 Bronze\nRaw and Immutable]
    SIL[🥈 Silver\nCleansed and Modeled]
    GLD[🥇 Gold\nCurated and Business Ready]
  end

  subgraph CONS[Consumption]
    direction TB
    SEM[🧠 Semantic Layer]
    BI[📊 BI / SQL / Reporting]
  end

  SYS --> CDC --> BRZ
  SYS --> BATCH --> BRZ
  MF --> BATCH --> BRZ
  BRZ --> SIL --> GLD --> SEM --> BI
  MF -. business fast path .-> GLD
