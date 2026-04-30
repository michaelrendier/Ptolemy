#include "ptolemy2.h"
#include "./ui_ptolemy2.h"

Ptolemy2::Ptolemy2(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::Ptolemy2)
{
    ui->setupUi(this);
}

Ptolemy2::~Ptolemy2()
{
    delete ui;
}
